from models.Order import Order, Channel, State
from models.DeliveryMan import DeliveryMan, Status
from structures.ProductList import ProductCatalog
from structures.RecipieList import RecipeDoubleList
from structures.OrderQueue import OrderQueue
from structures.LayerStack import LayerStack
from structures.DispatchList import DispatchList
from structures.TurnCircularList import TurnRing
from structures.DeliveryManList import CourierRing

PROMISE = {Channel.COUNTER: 8, Channel.DELIVERY: 20}

SAMPLE_CATALOG = [
    ("BRG-01", ["pan_base", "salsa", "carne", "queso", "cebolla", "tomate", "pan_tapa"]),
    ("BRG-02", ["pan_base", "salsa", "carne", "queso", "carne", "queso", "pan_tapa"]),
    ("CHK-01", ["pan_base", "salsa", "pollo", "lechuga", "tomate", "pan_tapa"]),
    ("VEG-01", ["pan_base", "salsa", "falafel", "lechuga", "cebolla", "tomate", "pan_tapa"]),
    ("BRG-01", ["pan_base", "salsa"]),   # duplicated, must be rejected
    ("EMP-01", []),                       # empty recipe, must be rejected
]

SAMPLE_ORDERS = [
    (Channel.COUNTER, "BRG-01", ["cebolla"], 600),
    (Channel.DELIVERY, "CHK-01", [], 601),
    (Channel.COUNTER, "BRG-02", [], 601),
    (Channel.COUNTER, "VEG-01", ["tomate"], 602),
    (Channel.COUNTER, "BRG-01", [], 603),
    (Channel.DELIVERY, "BRG-01", ["pepino"], 603),
    (Channel.COUNTER, "CHK-01", [], 604),
    (Channel.DELIVERY, "VEG-01", ["cebolla"], 605),
]

class Kitchen:
    def __init__(self, capacity:int = 4):
        self.catalog = ProductCatalog()
        self.queues = {Channel.COUNTER: OrderQueue(capacity), Channel.DELIVERY: OrderQueue(capacity)}
        self.turns = TurnRing()
        for channel in (Channel.COUNTER, Channel.COUNTER, Channel.COUNTER, Channel.DELIVERY):
            self.turns.insert_at_end(channel)
        self.couriers = CourierRing()
        self.bar = DispatchList()
        self.stack = LayerStack()
        self.current = None
        self.order_count = 0
        self.log = []
        # metrics
        self.attended = {Channel.COUNTER: 0, Channel.DELIVERY: 0}
        self.rejected = {Channel.COUNTER: 0, Channel.DELIVERY: 0}
        self.prep_times = {Channel.COUNTER: [], Channel.DELIVERY: []}
        self.on_time = {Channel.COUNTER: 0, Channel.DELIVERY: 0}
        self.ordered = {}
        self.product_errors = {}
        self.layer_errors = {}
        self.wasted = {}

    # ---------- helpers ----------
    def _done(self, ok:bool, msg:str):
        self.log.append(("OK  " if ok else "ERR ") + msg)
        return ok, msg

    def _count(self, counter:dict, key):
        counter[key] = counter.get(key, 0) + 1

    # expected layers of the order, from base to top
    def _expected(self, order:Order):
        recipe = self.catalog.find(order.product_code).recipe
        return [layer for layer in recipe.to_list() if layer not in order.without]

    # ---------- RF-01 ----------
    def load_catalog(self, data):
        loaded = 0
        rejected = []
        for code, ingredients in data:
            recipe = RecipeDoubleList()
            for ingredient in ingredients:
                recipe.append_ingredient(ingredient)
            if self.catalog.register_product(code, recipe):
                loaded += 1
            else:
                rejected.append(code)
        msg = f"Catálogo: {loaded} productos cargados"
        if rejected:
            msg += f"; rechazados (código duplicado o receta vacía): {', '.join(rejected)}"
        return self._done(True, msg)

    # ---------- RF-02 ----------
    def register_order(self, channel:Channel, code:str, without:list, minute:int):
        self.order_count += 1
        number = self.order_count
        product = self.catalog.find(code)
        if product is None:
            return self._done(False, f"Pedido {number} rechazado (RF-02): el producto {code} no existe")
        layers = product.recipe.to_list()
        for layer in without:
            if layer not in layers:
                return self._done(False, f"Pedido {number} rechazado (RF-02): la capa {layer} no está en la receta")
        order = Order(number, channel, code, without, minute)
        if not self.queues[channel].enqueue(order):
            self.rejected[channel] += 1
            return self._done(False, f"Pedido {number} rechazado (R7): la cola {channel.value} está llena")
        self._count(self.ordered, code)
        return self._done(True, f"Pedido {number} encolado en {channel.value}")

    # ---------- RF-03 (R2) ----------
    def next_order(self):
        if self.current is not None:
            return self._done(False, "Ya hay un pedido en armado: márquelo LISTO o cancélelo")
        turn = self.turns.current_chanel()
        other = Channel.DELIVERY if turn == Channel.COUNTER else Channel.COUNTER
        if not self.queues[turn].is_empty():
            chosen = turn
            why = f"le tocaba el turno de {turn.value} (R2)"
        elif not self.queues[other].is_empty():
            chosen = other
            why = f"la cola {turn.value} estaba vacía, se atiende {other.value} (R2)"
        else:
            return self._done(False, "No hay pedidos en espera")
        order = self.queues[chosen].dequeue()
        self.turns.advance()
        order.state = State.IN_ASSEMBLY
        self.current = order
        self.attended[chosen] += 1
        return self._done(True, f"Sale el pedido {order.number} ({order.product_code}) de la cola {chosen.value}: {why}")

    # ---------- RF-04 (R5) ----------
    def place_layer(self, layer:str):
        if self.current is None:
            return self._done(False, "No hay pedido en armado")
        if layer == "":
            return self._done(False, "Escriba la capa")
        expected = self._expected(self.current)
        pos = self.stack.size
        self.stack.push(layer)
        if pos >= len(expected) or expected[pos] != layer:
            self.current.errors += 1
            self._count(self.layer_errors, layer)
            self._count(self.product_errors, self.current.product_code)
            return self._done(False, f"Error de armado (R5): la capa {layer} no corresponde al paso {pos + 1}; no podrá cerrarse hasta corregir")
        return self._done(True, f"Capa {layer} colocada")

    # ---------- RF-05 (R3) ----------
    def remove_layer(self):
        layer = self.stack.pop()
        if layer is None:
            return self._done(False, "La pila está vacía (RF-05)")
        self._count(self.wasted, layer)
        return self._done(True, f"Capa {layer} retirada (desperdicio)")

    # layers of the stack from the top, with True if they are in the right place
    def stack_view(self):
        if self.current is None:
            return []
        expected = self._expected(self.current)
        layers = self.stack.to_list()
        n = len(layers)
        view = []
        for k, layer in enumerate(layers):
            pos = n - 1 - k
            view.append((layer, pos < len(expected) and expected[pos] == layer))
        return view

    # ---------- RF-06 ----------
    # both sequences are read from the top: the recipe with prev and the stack with next.
    # the part that sticks out (extra or missing layers) is on top, so it is skipped first
    def _check(self):
        stack_top = self.stack.to_list()
        recipe = self.catalog.find(self.current.product_code).recipe
        recipe_top = [l for l in recipe.to_list_reversed() if l not in self.current.without]
        n, m = len(stack_top), len(recipe_top)
        extra = stack_top[:n - m] if n > m else []
        missing = recipe_top[:m - n] if m > n else []
        a = stack_top[len(extra):]
        b = recipe_top[len(missing):]
        wrong = [f"{x} (esperaba {y})" for x, y in zip(a, b) if x != y]
        if not extra and not missing and not wrong:
            return True, "El armado coincide con la receta"
        parts = []
        if extra:
            parts.append("sobrantes: " + ", ".join(extra))
        if missing:
            parts.append("faltantes: " + ", ".join(missing))
        if wrong:
            parts.append("incorrectas: " + ", ".join(wrong))
        return False, "; ".join(parts)

    def verify(self):
        if self.current is None:
            return self._done(False, "No hay pedido en armado")
        ok, msg = self._check()
        return self._done(ok, "Verificación: " + msg)

    # ---------- RF-07 (R4, R8, R9) ----------
    def mark_ready(self, minute:int):
        if self.current is None:
            return self._done(False, "No hay pedido en armado")
        ok, msg = self._check()
        if not ok:
            return self._done(False, f"No se puede marcar LISTO (R4): {msg}")
        order = self.current
        order.state = State.READY
        order.ready_minute = minute
        total = minute - order.minute
        self.prep_times[order.channel].append(total)
        met = total <= PROMISE[order.channel]
        if met:
            self.on_time[order.channel] += 1
        self.bar.append(order)
        self.stack = LayerStack()
        self.current = None
        return self._done(True, f"Pedido {order.number} LISTO en {total} min ({'CUMPLE' if met else 'INCUMPLE'} la promesa de {PROMISE[order.channel]}, R8)")

    # ---------- RF-08 (R6) ----------
    def cancel_order(self):
        if self.current is None:
            return self._done(False, "No hay pedido en armado")
        while not self.stack.is_empty():
            self._count(self.wasted, self.stack.pop())
        order = self.current
        order.state = State.CANCELED
        self.current = None
        return self._done(True, f"Pedido {order.number} CANCELADO, pila vaciada capa por capa (R6)")

    # ---------- RF-09 ----------
    def bar_list(self, forward:bool = True):
        if forward:
            return self.bar.to_list()
        return self.bar.to_list_reversed()

    # ---------- RF-10 (R9, R10) ----------
    def deliver_counter(self, number:int):
        node = self.bar.find(number)
        if node is None:
            return self._done(False, f"El pedido {number} no está en la barra")
        if node.order.channel != Channel.COUNTER:
            return self._done(False, f"El pedido {number} es de DOMICILIO: use despachar (R9)")
        self.bar.remove(number)
        node.order.state = State.DELIVERED
        return self._done(True, f"Pedido {number} entregado en mostrador")

    def dispatch_delivery(self, number:int):
        node = self.bar.find(number)
        if node is None:
            return self._done(False, f"El pedido {number} no está en la barra")
        if node.order.channel != Channel.DELIVERY:
            return self._done(False, f"El pedido {number} es de MOSTRADOR: use entregar (R9)")
        start = self.couriers.current_delivery()
        if start is None:
            return self._done(False, "No hay repartidores en la ronda")
        while True:
            man = self.couriers.current_delivery().delivery_man
            if man.get_status() == Status.AVAILABLE:
                man.set_status(Status.EN_ROUTE)
                man.deliveries += 1
                self.couriers.advance()
                self.bar.remove(number)
                node.order.state = State.DELIVERED
                return self._done(True, f"Pedido {number} asignado a {man.code}")
            self.couriers.advance()
            # a full turn without finding one: stop
            if self.couriers.current_delivery() is start:
                return self._done(False, f"Todos los repartidores están EN_RUTA (R10): el pedido {number} sigue en la barra")

    # ---------- RF-11 ----------
    def register_return(self, code:str):
        node = self.couriers.find(code)
        if node is None:
            return self._done(False, f"El repartidor {code} no existe")
        if node.delivery_man.get_status() != Status.EN_ROUTE:
            return self._done(False, f"El repartidor {code} ya está disponible")
        node.delivery_man.set_status(Status.AVAILABLE)
        return self._done(True, f"{code} regresó y está DISPONIBLE")

    # ---------- RF-12 (R11) ----------
    def add_courier(self, code:str):
        if code == "":
            return self._done(False, "Escriba el código del repartidor")
        if self.couriers.find(code) is not None:
            return self._done(False, f"El repartidor {code} ya existe")
        self.couriers.add_at_end(DeliveryMan(code, Status.AVAILABLE, 0))
        return self._done(True, f"Repartidor {code} agregado a la ronda")

    def remove_courier(self, code:str):
        node = self.couriers.find(code)
        if node is None:
            return self._done(False, f"El repartidor {code} no existe")
        if node.delivery_man.get_status() == Status.EN_ROUTE:
            return self._done(False, f"No se puede retirar a {code}: está EN_RUTA (R11)")
        self.couriers.remove(code)
        return self._done(True, f"Repartidor {code} retirado de la ronda")

    # ---------- RF-13 ----------
    def report(self):
        def top(counter):
            if not counter:
                return "-"
            best = max(counter, key=counter.get)
            return f"{best} ({counter[best]})"

        lines = []
        for ch in Channel:
            times = self.prep_times[ch]
            avg = sum(times) / len(times) if times else 0
            pct = 100 * self.on_time[ch] / len(times) if times else 0
            lines.append(f"{ch.value}: atendidos {self.attended[ch]}, en cola {self.queues[ch].size}, "
                         f"rechazados por cola llena {self.rejected[ch]}")
            lines.append(f"   prep. promedio {avg:.1f} min, cumplimiento de promesa {pct:.0f}%")
        lines.append(f"Errores de armado (R5): {sum(self.layer_errors.values())}  por capa: {self.layer_errors}")
        lines.append(f"Capas desperdiciadas: {sum(self.wasted.values())}  por capa: {self.wasted}")
        lines.append(f"Producto más pedido: {top(self.ordered)}")
        lines.append(f"Producto con más errores: {top(self.product_errors)}")
        lines.append(f"Pedidos en la barra: {self.bar.size}")
        men = self.couriers.to_list() or []
        lines.append("Entregas por repartidor: " + (", ".join(f"{m.code}={m.deliveries}" for m in men) or "-"))
        lines.append(f"Puntero de turnos: {self.turns.current_chanel().value if not self.turns.is_empty() else '-'}")
        cur = self.couriers.current_delivery()
        lines.append(f"Puntero de la ronda: {cur.delivery_man.code if cur else '-'}")
        return "\n".join(lines)

    # ---------- sample data (RFE-09) ----------
    def load_sample(self):
        self.load_catalog(SAMPLE_CATALOG)
        for code in ("REP-1", "REP-2", "REP-3"):
            self.add_courier(code)
        for channel, code, without, minute in SAMPLE_ORDERS:
            self.register_order(channel, code, without, minute)
        return self._done(True, "Datos de ejemplo cargados")
