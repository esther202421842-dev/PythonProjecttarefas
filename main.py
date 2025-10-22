import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "todo.db"


def get_conn():
    return sqlite3.connect(str(DB_PATH))

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            vencimento TEXT,
            prioridade INTEGER DEFAULT 2,
            status TEXT DEFAULT 'todo',
            tags TEXT
        )
    """)
    conn.commit()
    conn.close()


def validar_fecha(fecha):
    """Devuelve True si fecha es None/vacía o si cumple AAAA-MM-DD."""
    if not fecha:
        return True
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def input_opcional(msg):
    v = input(msg).strip()
    return v if v else None

def input_prioridade(msg="Prioridade (1 = alta, 2 = média, 3 = baixa) [2]: "):
    v = input(msg).strip()
    if not v:
        return 2
    try:
        v = int(v)
    except ValueError:
        print("→ Use 1, 2 ou 3.")
        return input_prioridade(msg)
    if v not in (1, 2, 3):
        print("→ Use 1, 2 ou 3.")
        return input_prioridade(msg)
    return v

def input_data(msg="Vencimento (AAAA-MM-DD) [vazio=None]: "):
    v = input(msg).strip()
    if not v:
        return None
    if not validar_fecha(v):
        print("→ Formato inválido. Use AAAA-MM-DD (ex.: 2025-10-20).")
        return input_data(msg)
    return v

def print_tabela(rows):
    if not rows:
        print("Nenhuma tarefa registrada.")
        return
    headers = ["id","titulo","descricao","vencimento","prioridade","status","tags"]
    widths  = [4, 24, 28, 12, 10, 10, 18]

    def fmt(cols):
        out = []
        for (val, w) in zip(cols, widths):
            s = "" if val is None else str(val)
            if len(s) > w:
                s = s[:w-1] + "…"
            out.append(s.ljust(w))
        return " | ".join(out)

    print("\n" + fmt(headers))
    print("-" * (sum(widths) + 3*(len(widths)-1)))
    for r in rows:
        print(fmt(r))
    print()


def create_task():
    print("\n== Criar tarefa ==")
    titulo = input("Título (obrigatório): ").strip()
    if not titulo:
        print("→ Título é obrigatório. Operação cancelada.\n")
        return
    descricao  = input_opcional("Descrição (opcional): ")
    vencimento = input_data()
    prioridade = input_prioridade()
    tags       = input_opcional("Tags (CSV, ex.: faculdade,LES) [opcional]: ")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (titulo, descricao, vencimento, prioridade, tags) VALUES (?,?,?,?,?)",
        (titulo, descricao, vencimento, prioridade, tags)
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    print("→ Tarefa criada com id {}.\n".format(task_id))

def _query_tasks(where_sql="", params=()):
    conn = get_conn()
    cur = conn.cursor()
    base = "SELECT * FROM tasks"
    if where_sql:
        base += " WHERE " + where_sql
    base += " ORDER BY prioridade ASC, id DESC"
    cur.execute(base, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def list_tasks():
    print("\n== Listar tarefas ==")
    # Filtros opcionais
    f_status = input("Filtrar por status [vazio=sem filtro | todo/doing/done]: ").strip()
    status = f_status if f_status in ("todo","doing","done") else None

    f_prio = input("Filtrar por prioridade [vazio=sem filtro | 1/2/3]: ").strip()
    prioridade = None
    if f_prio:
        try:
            pv = int(f_prio)
            if pv in (1,2,3):
                prioridade = pv
        except ValueError:
            pass

    f_tag = input("Filtrar por tag ").strip()
    taglike = "%{}%".format(f_tag) if f_tag else None

    where = []
    params = []
    if status:
        where.append("status=?"); params.append(status)
    if prioridade is not None:
        where.append("prioridade=?"); params.append(prioridade)
    if taglike:
        where.append("(tags LIKE ?)"); params.append(taglike)

    where_sql = " AND ".join(where)
    rows = _query_tasks(where_sql, tuple(params))
    print_tabela(rows)

    # Resumo rápido
    total = _count_all()
    c_todo, c_doing, c_done = _count_by_status()
    print("Resumo: total={} | todo={} | doing={} | done={}\n".format(total, c_todo, c_doing, c_done))

def update_task():
    print("\n== Editar tarefa ==")
    try:
        task_id = int(input("ID da tarefa: ").strip())
    except ValueError:
        print("→ ID inválido.\n"); return

    titulo    = input_opcional("Novo título [enter=manter]: ")
    if titulo is not None and not titulo.strip():
        print("→ Título não pode ser vazio.\n"); return
    descricao = input_opcional("Nova descrição [enter=manter]: ")
    vencimento= input_data("Novo vencimento (AAAA-MM-DD) [enter=manter]: ")
    pr_raw    = input("Nova prioridade (1/2/3) [enter=manter]: ").strip()
    prioridade= None
    if pr_raw:
        try:
            pr = int(pr_raw)
            if pr not in (1,2,3):
                raise ValueError
            prioridade = pr
        except ValueError:
            print("→ Prioridade deve ser 1, 2 ou 3.\n"); return
    st_raw    = input("Novo status (todo/doing/done) [enter=manter]: ").strip()
    status    = st_raw if st_raw in ("todo","doing","done") else None
    tags      = input_opcional("Novas tags (CSV) [enter=manter]: ")

    fields = {}
    if titulo is not None:     fields["titulo"] = titulo
    if descricao is not None:  fields["descricao"] = descricao
    if vencimento is not None: fields["vencimento"] = vencimento
    if prioridade is not None: fields["prioridade"] = prioridade
    if status is not None:     fields["status"] = status
    if tags is not None:       fields["tags"] = tags
    if not fields:
        print("→ Nada para atualizar.\n"); return

    sets = ", ".join(["{}=?".format(k) for k in fields.keys()])
    values = list(fields.values()) + [task_id]

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET {} WHERE id=?".format(sets), values)
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    print("→ Atualizada!\n" if ok else "→ Não encontrada.\n")

def delete_task():
    print("\n== Excluir tarefa ==")
    try:
        task_id = int(input("ID da tarefa: ").strip())
    except ValueError:
        print("→ ID inválido.\n"); return
    conf = input("Tem certeza? digite 'SIM' para confirmar: ").strip()
    if conf != "SIM":
        print("→ Exclusão cancelada.\n"); return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    print("→ Removida!\n" if ok else "→ Não encontrada.\n")

def mark_done():
    print("\n== Concluir tarefa ==")
    try:
        task_id = int(input("ID da tarefa: ").strip())
    except ValueError:
        print("→ ID inválido.\n"); return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    print("→ Concluída!\n" if ok else "→ Não encontrada.\n")

def _count_all():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks")
    n = cur.fetchone()[0]
    conn.close()
    return n

def _count_by_status():
    conn = get_conn()
    cur = conn.cursor()
    counts = {}
    for s in ("todo","doing","done"):
        cur.execute("SELECT COUNT(*) FROM tasks WHERE status=?", (s,))
        counts[s] = cur.fetchone()[0]
    conn.close()
    return counts.get("todo",0), counts.get("doing",0), counts.get("done",0)

def kanban_view():
    print("\n== Resumo / Kanban ==")
    c_todo, c_doing, c_done = _count_by_status()
    total = _count_all()
    print("Total: {}  |  todo: {}  |  doing: {}  |  done: {}\n".format(total, c_todo, c_doing, c_done))

    def show(col_status, titulo_col):
        rows = _query_tasks("status=?", (col_status,))
        print("[{}] ({})".format(titulo_col, len(rows)))
        if not rows:
            print("  — vazio —")
        else:
            for r in rows:
                _id, tit, desc, venc, prio, st, tags = r
                linha = "  #{}  {}".format(_id, tit)
                if venc: linha += "  (venc: {})".format(venc)
                if prio: linha += "  [p{}]".format(prio)
                print(linha)
        print()

    show("todo",  "TODO")
    show("doing", "DOING")
    show("done",  "DONE")


def menu():
    while True:
        print("==== Mini Gestor de Tarefas ====")
        print("1 - Criar tarefa")
        print("2 - Listar tarefas")
        print("3 - Editar tarefa")
        print("4 - Concluir tarefa")
        print("5 - Excluir tarefa")
        print("6 - Resumo ")
        print("0 - Sair")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            create_task()
        elif op == "2":
            list_tasks()
        elif op == "3":
            update_task()
        elif op == "4":
            mark_done()
        elif op == "5":
            delete_task()
        elif op == "6":
            kanban_view()
        elif op == "0":
            print("Até mais!")
            break
        else:
            print("→ Opção inválida.\n")


if __name__ == "__main__":
    init_db()
    menu()