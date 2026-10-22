import tkinter as tk
from tkinter import ttk
from kitchen import Kitchen
from models.Order import Channel

k = Kitchen()

root = tk.Tk()
root.title("Cocina de comida rápida")
root.geometry("900x650")

msg_var = tk.StringVar()
msg_lbl = tk.Label(root, textvariable=msg_var, anchor="w", font=("Arial", 11, "bold"))
msg_lbl.pack(fill="x", padx=8, pady=4)

top = tk.Frame(root)
top.pack(fill="x", padx=8)
tk.Label(top, text="Minuto actual:").pack(side="left")
minute_var = tk.StringVar(value="600")
tk.Entry(top, textvariable=minute_var, width=8).pack(side="left", padx=4)

tabs = ttk.Notebook(root)
tabs.pack(fill="both", expand=True, padx=8, pady=8)

bar_forward = [True]


def new_tab(title):
    frame = tk.Frame(tabs)
    tabs.add(frame, text=title)
    return frame


def text_box(parent, height):
    box = tk.Text(parent, height=height, font=("Consolas", 10), state="disabled")
    box.pack(fill="both", expand=True, padx=4, pady=4)
    return box


def show(box, content):
    box.config(state="normal")
    box.delete("1.0", "end")
    box.insert("1.0", content)
    box.config(state="disabled")


def row(parent):
    frame = tk.Frame(parent)
    frame.pack(fill="x", padx=4, pady=2)
    return frame


def button(parent, text, command):
    tk.Button(parent, text=text, command=command).pack(side="left", padx=3)


def get_minute():
    try:
        return int(minute_var.get())
    except ValueError:
        return None


def get_number(var):
    try:
        return int(var.get())
    except ValueError:
        return None


def act(result):
    ok, msg = result
    msg_var.set(msg)
    msg_lbl.config(fg="green" if ok else "red")
    refresh()


def fail(msg):
    act((False, msg))


# ---------------- 1. Toma de pedido ----------------
t1 = new_tab("1. Toma de pedido")
r = row(t1)
tk.Label(r, text="Canal").pack(side="left")
channel_cb = ttk.Combobox(r, values=[c.value for c in Channel], width=12, state="readonly")
channel_cb.current(0)
channel_cb.pack(side="left", padx=4)
tk.Label(r, text="Producto").pack(side="left")
product_cb = ttk.Combobox(r, width=10, state="readonly")
product_cb.pack(side="left", padx=4)
tk.Label(r, text="Sin (separado por comas)").pack(side="left")
without_var = tk.StringVar()
tk.Entry(r, textvariable=without_var, width=20).pack(side="left", padx=4)


def register_order():
    minute = get_minute()
    if minute is None:
        return fail("Minuto inválido")
    without = [x.strip() for x in without_var.get().split(",") if x.strip()]
    act(k.register_order(Channel(channel_cb.get()), product_cb.get(), without, minute))


r = row(t1)
button(r, "Registrar pedido", register_order)
button(r, "Cargar datos de ejemplo", lambda: act(k.load_sample()))
catalog_box = text_box(t1, 15)

# ---------------- 2. Cocina ----------------
t2 = new_tab("2. Cocina")
r = row(t2)
button(r, "Llamar siguiente pedido", lambda: act(k.next_order()))
kitchen_box = text_box(t2, 15)

# ---------------- 3. Armado ----------------
t3 = new_tab("3. Armado")
r = row(t3)
layer_var = tk.StringVar()
tk.Label(r, text="Capa").pack(side="left")
tk.Entry(r, textvariable=layer_var, width=14).pack(side="left", padx=4)
button(r, "Colocar", lambda: act(k.place_layer(layer_var.get().strip())))
button(r, "Retirar", lambda: act(k.remove_layer()))
button(r, "Verificar", lambda: act(k.verify()))


def mark_ready():
    minute = get_minute()
    if minute is None:
        return fail("Minuto inválido")
    act(k.mark_ready(minute))


button(r, "Marcar LISTO", mark_ready)
button(r, "Cancelar pedido", lambda: act(k.cancel_order()))
assembly_box = text_box(t3, 15)

# ---------------- 4. Despacho ----------------
t4 = new_tab("4. Despacho")
r = row(t4)


def set_direction(forward):
    bar_forward[0] = forward
    refresh()


button(r, "Recorrer cabeza → cola", lambda: set_direction(True))
button(r, "Recorrer cola → cabeza", lambda: set_direction(False))
r = row(t4)
number_var = tk.StringVar()
tk.Label(r, text="Pedido N°").pack(side="left")
tk.Entry(r, textvariable=number_var, width=6).pack(side="left", padx=4)


def with_number(action):
    number = get_number(number_var)
    if number is None:
        return fail("Número de pedido inválido")
    act(action(number))


button(r, "Entregar en mostrador", lambda: with_number(k.deliver_counter))
button(r, "Despachar domicilio", lambda: with_number(k.dispatch_delivery))
r = row(t4)
courier_var = tk.StringVar()
tk.Label(r, text="Repartidor").pack(side="left")
tk.Entry(r, textvariable=courier_var, width=8).pack(side="left", padx=4)
button(r, "Agregar", lambda: act(k.add_courier(courier_var.get().strip())))
button(r, "Retirar", lambda: act(k.remove_courier(courier_var.get().strip())))
button(r, "Registrar regreso", lambda: act(k.register_return(courier_var.get().strip())))
dispatch_box = text_box(t4, 15)

# ---------------- 5. Reportes y bitácora ----------------
t5 = new_tab("5. Reportes y bitácora")
report_box = text_box(t5, 12)
log_box = text_box(t5, 10)


# ---------------- refresh ----------------
def order_text(order):
    return f"#{order.number} {order.product_code}"


def refresh():
    product_cb["values"] = [p.code for p in k.catalog.to_array()]
    if product_cb.get() == "" and product_cb["values"]:
        product_cb.current(0)

    # 1
    lines = []
    for p in k.catalog.to_array():
        steps = ", ".join(f"{i + 1}.{x}" for i, x in enumerate(p.recipe.to_list()))
        lines.append(f"{p.code}: {steps}")
    show(catalog_box, "\n".join(lines))

    # 2
    lines = []
    for ch in Channel:
        q = k.queues[ch]
        items = "  ".join(f"[{order_text(o)}]" for o in q.to_list()) or "(vacía)"
        lines.append(f"{ch.value}  ({q.size}/{q.capacity})")
        lines.append(f"  FRENTE -> {items} <- FINAL")
        lines.append("")
    ring = k.turns.to_list() or []
    shown = " -> ".join(c.value for c in ring)
    lines.append("Anillo de turnos (el primero es el PUNTERO):")
    lines.append(f"  ▶ {shown} -> (vuelve al primero)")
    show(kitchen_box, "\n".join(lines))

    # 3
    lines = []
    if k.current is None:
        lines.append("No hay pedido en armado")
    else:
        o = k.current
        product = k.catalog.find(o.product_code)
        recipe = ", ".join(f"{i + 1}.{x}" for i, x in enumerate(product.recipe.to_list()))
        lines.append(f"Pedido #{o.number} {o.product_code} ({o.channel.value})  sin: {', '.join(o.without) or '-'}")
        lines.append(f"Receta (base -> tapa): {recipe}")
        lines.append(f"Errores de armado en este pedido: {o.errors}")
        lines.append("")
        lines.append("PILA (tope arriba):")
        for layer, ok in k.stack_view():
            lines.append(f"  | {layer:<12}|" + ("" if ok else "   <-- FUERA DE ORDEN (R5)"))
        lines.append("  +-- BASE --+")
    show(assembly_box, "\n".join(lines))

    # 4
    orders = k.bar_list(bar_forward[0])
    items = " <-> ".join(f"[{order_text(o)} {o.channel.value}]" for o in orders) or "(vacía)"
    if bar_forward[0]:
        bar = f"CABEZA -> {items} <- COLA   ({k.bar.size})"
    else:
        bar = f"COLA -> {items} <- CABEZA   ({k.bar.size})"
    lines = ["BARRA DE DESPACHO", bar, "", "RONDA DE REPARTIDORES (el primero es el PUNTERO):"]
    for i, m in enumerate(k.couriers.to_list() or []):
        mark = "▶" if i == 0 else " "
        lines.append(f"  {mark} {m.code}  {m.get_status().value}  entregas: {m.deliveries}")
    lines.append("  (después del último vuelve al primero)")
    show(dispatch_box, "\n".join(lines))

    # 5
    show(report_box, k.report())
    show(log_box, "\n".join(k.log))


refresh()
root.mainloop()
