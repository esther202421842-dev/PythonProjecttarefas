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

def input_prioridade(msg="Prioridade (1 = alta, 2 = média, 3 = baixa): "):
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

def input_data(msg="Vencimento (AAAA-MM-DD): "):
    v = input(msg).strip()
    if not v:
        return None
    if not validar_fecha(v):
        print("→ Formato inválido. Use AAAA-MM-DD.")
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
        print("→ Título é obrigatório.\n")
        return
    descricao  = input_opcional("Descrição: ")
    vencimento = input_data()
    prioridade = input_prioridade()
    tags       = input_opcional("Tags (CSV): ")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (titulo, descricao, vencimento, prioridade, tags) VALUES (?,?,?,?,?)",
        (titulo, descricao, vencimento, prioridade, tags)
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    print(f"→ Tarefa criada com id {task_id}.\n")

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
    print("""
Escolha um filtro:
1 - Status
2 - Prioridade
3 - Tag
4 - Ver tudo (sem filtros)
0 - Voltar
""")

    opc = input("Opção: ").strip()
    where = []
    params = []

    if opc == "1":
        print("""
Status:
1 - todo
2 - doing
3 - done
""")
        sel = input("Escolha: ").strip()
        status_map = {"1": "todo", "2": "doing", "3": "done"}
        if sel in status_map:
            where.append("status=?")
            params.append(status_map[sel])

    elif opc == "2":
        print("""
Prioridade:
1 - Alta
2 - Média
3 - Baixa
""")
        sel = input("Escolha: ").strip()
        if sel in ("1","2","3"):
            where.append("prioridade=?")
            params.append(int(sel))

    elif opc == "3":
        tag = input("Digite a tag: ").strip()
        if tag:
            where.append("tags LIKE ?")
            params.append(f"%{tag}%")

    elif opc == "4":
        pass

    elif opc == "0":
        print()
        return

    else:
        print("→ Opção inválida\n")
        return

    where_sql = " AND ".join(where)
    rows = _query_tasks(where_sql, tuple(params))
    print_tabela(rows)

    total = _count_all()
    c_todo, c_doing, c_done = _count_by_status()
    print(f"Resumo: total={total} | todo={c_todo} | doing={c_doing} | done={c_done}\n")

def buscar_tarefa():
    termo = input("\nDigite palavra-chave: ").strip()
    if not termo:
        print("→ Informe um termo.\n")
        return
    like = f"%{termo}%"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM tasks WHERE titulo LIKE ? OR descricao LIKE ? OR tags LIKE ? ORDER BY prioridade ASC, id DESC",
        (like, like, like)
    )
    resultados = cur.fetchall()
    conn.close()

    if not resultados:
        print("Nenhuma tarefa encontrada.\n")
        return

    print_tabela(resultados)

def update_task():
    print("\n== Editar tarefa ==")
    try:
        task_id = int(input("ID da tarefa: ").strip())
    except ValueError:
        print("→ ID inválido.\n"); return

    titulo    = input_opcional("Novo título: ")
    if titulo is not None and not titulo.strip():
        print("→ Título não pode ser vazio.\n"); return
    descricao = input_opcional("Nova descrição: ")
    vencimento= input_data("Novo vencimento (AAAA-MM-DD): ")
    pr_raw    = input("Nova prioridade (1/2/3): ").strip()
    prioridade = None
    if pr_raw:
        try:
            p = int(pr_raw)
            if p not in (1,2,3):
                raise ValueError
            prioridade = p
        except ValueError:
            print("→ Prioridade inválida.\n"); return
    st_raw = input("Novo status (todo/doing/done): ").strip()
    status = st_raw if st_raw in ("todo","doing","done") else None
    tags   = input_opcional("Novas tags: ")

    fields = {}
    if titulo is not None: fields["titulo"] = titulo
    if descricao is not None: fields["descricao"] = descricao
    if vencimento is not None: fields["vencimento"] = vencimento
    if prioridade is not None: fields["prioridade"] = prioridade
    if status is not None: fields["status"] = status
    if tags is not None: fields["tags"] = tags
    if not fields:
        print("→ Nada para atualizar.\n"); return

    sets = ", ".join([f"{k}=?" for k in fields.keys()])
    values = list(fields.values()) + [task_id]

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"UPDATE tasks SET {sets} WHERE id=?", values)
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
    conf = input("Tem certeza? digite 'SIM': ").strip()
    if conf != "SIM":
        print("→ Cancelado.\n"); return
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
    print(f"Total: {total}  |  todo: {c_todo}  |  doing: {c_doing}  |  done: {c_done}\n")

def menu():
    while True:
        print("""==== Mini Gestor de Tarefas ====
1 - Criar tarefa
2 - Listar tarefas (com filtros)
3 - Editar tarefa
4 - Concluir tarefa
5 - Excluir tarefa
6 - Resumo
7 - Buscar tarefa (palavra-chave)
0 - Sair
""")
        op = input("Escolha: ").strip()
        if op == "1": create_task()
        elif op == "2": list_tasks()
        elif op == "3": update_task()
        elif op == "4": mark_done()
        elif op == "5": delete_task()
        elif op == "6": kanban_view()
        elif op == "7": buscar_tarefa()
        elif op == "0":
            print("Até mais!")
            break
        else:
            print("→ Opção inválida.\n")

if __name__ == "__main__":
    init_db()
    menu()