import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import time


# ============================================================
# ALAPÉRTÉKEK
# ============================================================

DEFAULTS = {
    "width": 900,
    "height": 650,

    "start_bacteria": 25,
    "max_bacteria": 250,

    "start_food": 140,
    "max_food": 300,
    "food_energy": 85,
    "food_spawn_chance": 0.20,

    "initial_energy": 120,
    "max_energy": 300,

    # Szaporodás
    "reproduction_cost": 30,
    "offspring_energy": 70,
    "mating_distance": 25,

    # Mutáció
    "mutation_chance": 0.08,
    "mutation_strength": 0.08,

    # Életkor
    "max_age": 250,
}


# ============================================================
# SEGÉDFÜGGVÉNYEK
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def mutate_gene(value, minimum, maximum, mutation_chance, mutation_strength):
    if random.random() < mutation_chance:
        mutation = random.gauss(0, max(abs(value) * mutation_strength, 0.01))
        value += mutation
    return clamp(value, minimum, maximum)


# ============================================================
# ÉTEL
# ============================================================

class Food:

    def __init__(self, width, height):
        self.x = random.uniform(15, width - 15)
        self.y = random.uniform(15, height - 15)
        self.phase = random.uniform(0, math.tau)

    def update(self, dt):
        self.phase += dt * 3

    def draw(self, canvas):
        pulse = (math.sin(self.phase) + 1) / 2
        size = 3.5 + pulse * 1.5

        canvas.create_oval(
            self.x - size, self.y - size,
            self.x + size, self.y + size,
            fill="#44ff77", outline="#1e5230"
        )


# ============================================================
# BAKTÉRIUM (PONTOS GENETIKÁVAL ÉS FIX SZÍNNEL)
# ============================================================

class Bacteria:

    next_id = 0

    def __init__(self, x, y, settings, genes=None, generation=0, color=None):
        self.x = x
        self.y = y
        self.settings = settings
        self.energy = settings["initial_energy"]
        self.age = 0
        self.generation = generation

        self.id = Bacteria.next_id
        Bacteria.next_id += 1

        self.mating_cooldown = random.uniform(0, 2)
        self.mating_flash = 0
        self.wiggle_phase = random.uniform(0, math.tau)

        # ----------------------------------------------------
        # GENETIKAI TULAJDONSÁGOK (GÉNEK)
        # ----------------------------------------------------
        if genes is None:
            self.speed = random.uniform(1.2, 2.2)               # Sebesség
            self.size = random.uniform(5.0, 8.0)                # Méret
            self.sense = random.uniform(60, 130)                # Látótávolság / Érzékelés
            self.mating_propensity = random.uniform(0.3, 0.9)   # Párosodási hajlam (0-1)
            self.efficiency = random.uniform(0.7, 1.2)          # Emésztési hatékonyság
            
            # Véletlenszerű fix törzsszín az első generációnak
            self.color = f"#{random.randint(50, 240):02x}{random.randint(50, 240):02x}{random.randint(150, 255):02x}"
        else:
            m_chance = settings["mutation_chance"]
            m_str = settings["mutation_strength"]

            # Örökölt gének mutációval
            self.speed = mutate_gene(genes["speed"], 0.5, 4.0, m_chance, m_str)
            self.size = mutate_gene(genes["size"], 3.5, 12.0, m_chance, m_str)
            self.sense = mutate_gene(genes["sense"], 30, 220, m_chance, m_str)
            self.mating_propensity = mutate_gene(genes["mating_propensity"], 0.1, 1.0, m_chance, m_str)
            self.efficiency = mutate_gene(genes["efficiency"], 0.5, 1.5, m_chance, m_str)
            
            # A szülői törzsszín öröklése (kisebb árnyalatnyi mutációval)
            self.color = color if color else "#5599ff"

        self.angle = random.uniform(0, math.tau)
        self.direction_timer = random.uniform(0.5, 2.0)

    def get_genes(self):
        return {
            "speed": self.speed,
            "size": self.size,
            "sense": self.sense,
            "mating_propensity": self.mating_propensity,
            "efficiency": self.efficiency
        }

    def move(self, foods, bacteria_list, dt):
        self.age += dt
        self.mating_cooldown = max(0, self.mating_cooldown - dt)
        self.mating_flash = max(0, self.mating_flash - dt)
        self.wiggle_phase += dt * self.speed * 8.0

        # Keresés a LÁTÓTÁVOLSÁGON (sense) belül
        closest_food = None
        closest_food_dist = self.sense

        for food in foods:
            d = distance(food.x, food.y, self.x, self.y)
            if d < closest_food_dist:
                closest_food_dist = d
                closest_food = food

        closest_partner = None
        closest_partner_dist = self.sense

        # Párosodási küszöb a Párosodási Hajlam (mating_propensity) alapján
        required_energy = self.settings["initial_energy"] * (1.5 - self.mating_propensity * 0.7)

        if self.energy >= required_energy and self.mating_cooldown <= 0:
            for other in bacteria_list:
                if other is self or other.mating_cooldown > 0:
                    continue
                d = distance(self.x, self.y, other.x, other.y)
                if d < self.sense and d < closest_partner_dist:
                    closest_partner_dist = d
                    closest_partner = other

        # Navigáció
        if closest_partner:
            target_angle = math.atan2(closest_partner.y - self.y, closest_partner.x - self.x)
            self.angle = self.angle * 0.85 + target_angle * 0.15
        elif closest_food:
            target_angle = math.atan2(closest_food.y - self.y, closest_food.x - self.x)
            self.angle = target_angle
        else:
            self.direction_timer -= dt
            if self.direction_timer <= 0:
                self.angle += random.uniform(-0.8, 0.8)
                self.direction_timer = random.uniform(0.5, 2.0)

        self.x += math.cos(self.angle) * self.speed * dt * 60
        self.y += math.sin(self.angle) * self.speed * dt * 60

        # Falak
        margin = 10
        if self.x < margin:
            self.x = margin
            self.angle = random.uniform(-math.pi / 2, math.pi / 2)
        elif self.x > self.settings["width"] - margin:
            self.x = self.settings["width"] - margin
            self.angle = random.uniform(math.pi / 2, 3 * math.pi / 2)

        if self.y < margin:
            self.y = margin
            self.angle = random.uniform(0, math.pi)
        elif self.y > self.settings["height"] - margin:
            self.y = self.settings["height"] - margin
            self.angle = random.uniform(math.pi, math.tau)

        # ----------------------------------------------------
        # TERMÉSZETES SZELEKCIÓ / ENERGIAKÖLTSÉGEK
        # A jobb fenotípusok drágábbak anyagcserében!
        # ----------------------------------------------------
        speed_cost = (self.speed ** 2.0) * 0.009
        size_cost = (self.size ** 1.2) * 0.006
        sense_cost = self.sense * 0.0003
        efficiency_cost = (self.efficiency ** 1.5) * 0.005  # A jobb emésztőrendszer fenntartása is drága
        base_cost = 0.015

        total_cost = base_cost + speed_cost + size_cost + sense_cost + efficiency_cost
        self.energy -= total_cost * dt * 60

    def eat(self, foods):
        eaten = 0
        for food in foods[:]:
            d = distance(food.x, food.y, self.x, self.y)
            if d < self.size + 5:
                foods.remove(food)
                # Az emésztési hatékonyság (efficiency) növeli a nyert energiát
                gained_energy = self.settings["food_energy"] * self.efficiency
                self.energy = min(self.energy + gained_energy, self.settings["max_energy"])
                eaten += 1
        return eaten

    def can_reproduce_with(self, other):
        req_self = self.settings["initial_energy"] * (1.5 - self.mating_propensity * 0.7)
        req_other = other.settings["initial_energy"] * (1.5 - other.mating_propensity * 0.7)

        if other is self or self.energy < req_self or other.energy < req_other:
            return False
        if self.mating_cooldown > 0 or other.mating_cooldown > 0:
            return False
        return distance(self.x, self.y, other.x, other.y) <= self.settings["mating_distance"]

    def reproduce_with(self, other):
        if not self.can_reproduce_with(other):
            return None

        self.energy -= self.settings["reproduction_cost"]
        other.energy -= self.settings["reproduction_cost"]

        pa, pb = self.get_genes(), other.get_genes()
        
        # PONTOS GENETIKAI ÖRÖKLŐDÉS:
        # Minden gént 50-50% eséllyel kap az egyik vagy a másik szülőtől!
        child_genes = {k: pa[k] if random.random() < 0.5 else pb[k] for k in pa}

        cx = clamp((self.x + other.x) / 2 + random.uniform(-8, 8), 10, self.settings["width"] - 10)
        cy = clamp((self.y + other.y) / 2 + random.uniform(-8, 8), 10, self.settings["height"] - 10)

        # Domináns szülő színének öröklése
        child_color = self.color if random.random() < 0.5 else other.color

        child = Bacteria(
            cx, cy, self.settings,
            genes=child_genes,
            generation=max(self.generation, other.generation) + 1,
            color=child_color
        )
        child.energy = self.settings["offspring_energy"]

        self.mating_cooldown = 3.0
        other.mating_cooldown = 3.0
        self.mating_flash = 0.4
        other.mating_flash = 0.4

        return child

    def is_dead(self):
        return self.energy <= 0 or self.age >= self.settings["max_age"]

    def draw(self, canvas, show_sense=False, show_energy=True):
        # Nincs elszíneződés haldokláskor: A saját FIX SZÍNÉT használja!
        main_color = self.color

        if show_sense:
            canvas.create_oval(
                self.x - self.sense, self.y - self.sense,
                self.x + self.sense, self.y + self.sense,
                outline="#1e2638", width=1
            )

        if self.mating_flash > 0:
            rad = self.size + 8
            canvas.create_oval(self.x - rad, self.y - rad, self.x + rad, self.y + rad, outline="#ffff66", width=2)

        # 1. Flagella (Ostor)
        tail_len = self.size * 2.2
        for offset_angle in [-0.2, 0.2]:
            t_angle = self.angle + math.pi + offset_angle
            wave = math.sin(self.wiggle_phase + offset_angle * 5) * 5
            
            tx1 = self.x + math.cos(t_angle) * (self.size * 0.8)
            ty1 = self.y + math.sin(t_angle) * (self.size * 0.8)
            tx2 = self.x + math.cos(t_angle) * tail_len + math.cos(self.angle + math.pi/2) * wave
            ty2 = self.y + math.sin(t_angle) * tail_len + math.sin(self.angle + math.pi/2) * wave

            canvas.create_line(tx1, ty1, tx2, ty2, fill="#445566", width=1.5)

        # 2. Sejttest
        rx = self.size * 1.3
        ry = self.size * 0.85
        cos_a, sin_a = math.cos(self.angle), math.sin(self.angle)
        poly_points = []
        steps = 12
        for i in range(steps):
            theta = (i / steps) * math.tau
            px = rx * math.cos(theta)
            py = ry * math.sin(theta)
            rot_x = self.x + px * cos_a - py * sin_a
            rot_y = self.y + px * sin_a + py * cos_a
            poly_points.extend([rot_x, rot_y])

        canvas.create_polygon(poly_points, fill=main_color, outline="#ffffff", width=1.2, smooth=True)

        # 3. Belső Mag
        cr = self.size * 0.3
        canvas.create_oval(self.x - cr, self.y - cr, self.x + cr, self.y + cr, fill="#ffffff", outline="")

        if show_energy:
            e_ratio = clamp(self.energy / self.settings["max_energy"], 0, 1)
            bw, bh = 20, 3
            ew = bw * e_ratio
            canvas.create_rectangle(self.x - bw/2, self.y - ry - 8, self.x + bw/2, self.y - ry - 8 + bh, fill="#222222", outline="")
            canvas.create_rectangle(self.x - bw/2, self.y - ry - 8, self.x - bw/2 + ew, self.y - ry - 8 + bh, fill="#55ff88", outline="")


# ============================================================
# FŐ ALKALMAZÁS GUI
# ============================================================

class Simulation:

    def __init__(self, root):
        self.root = root
        self.root.title("Evolúciós Szimulátor")
        self.root.resizable(True, True)

        self.settings = DEFAULTS.copy()
        self.running = True
        self.speed_multiplier = 1.0
        self.last_time = time.perf_counter()

        self.generation = 0
        self.total_births = 0
        self.total_deaths = 0

        # Kezdettől fogva megőrzött történet a grafikonhoz
        self.history = {
            "time": [],
            "population": [],
            "speed": [],
            "size": [],
            "sense": [],
            "mating_propensity": [],
            "efficiency": [],
        }
        self.elapsed_time = 0.0

        main_frame = tk.Frame(root, bg="#0b0e14")
        main_frame.pack(fill="both", expand=True)

        left_frame = tk.Frame(main_frame, bg="#0b0e14")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.canvas = tk.Canvas(
            left_frame,
            width=self.settings["width"],
            height=self.settings["height"],
            bg="#0d1117",
            highlightthickness=1,
            highlightbackground="#21262d"
        )
        self.canvas.pack(fill="both", expand=True)

        right_container = tk.Frame(main_frame, bg="#161b22", width=340)
        right_container.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        side_canvas = tk.Canvas(right_container, bg="#161b22", highlightthickness=0, width=320)
        scrollbar = tk.Scrollbar(right_container, orient="vertical", command=side_canvas.yview)
        
        right_frame = tk.Frame(side_canvas, bg="#161b22")
        right_frame.bind("<Configure>", lambda e: side_canvas.configure(scrollregion=side_canvas.bbox("all")))

        side_canvas.create_window((0, 0), window=right_frame, anchor="nw")
        side_canvas.configure(yscrollcommand=scrollbar.set)

        side_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            side_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        side_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # VEZÉRLŐK
        tk.Label(right_frame, text="🧬 EVOLÚCIÓS\nSZIMULÁTOR", bg="#161b22", fg="white", font=("Arial", 14, "bold")).pack(pady=(12, 8))

        self.stats_label = tk.Label(right_frame, text="", bg="#161b22", fg="#dddddd", justify="left", anchor="w", font=("Consolas", 8))
        self.stats_label.pack(padx=10, pady=2, fill="x")

        # Étel csúszka
        food_box = tk.LabelFrame(right_frame, text="🍏 Étel Kínálat", bg="#161b22", fg="#44ff77", font=("Arial", 9, "bold"))
        food_box.pack(fill="x", padx=10, pady=6)

        self.food_slider = tk.Scale(
            food_box, from_=0, to=15, orient="horizontal", bg="#161b22", fg="white",
            highlightthickness=0, command=self.on_food_slider_change
        )
        self.food_slider.set(self.settings["food_spawn_chance"] * 100)
        self.food_slider.pack(fill="x", padx=5, pady=2)

        tk.Button(food_box, text="+ Étel szórása", command=self.add_instant_food, bg="#238636", fg="white", font=("Arial", 8, "bold")).pack(pady=4)

        # Gombok
        self.pause_button = tk.Button(right_frame, text="⏸ Szünet", command=self.toggle_pause, width=24)
        self.pause_button.pack(pady=2)

        tk.Button(right_frame, text="⏩ Gyorsítás", command=self.increase_speed, width=24).pack(pady=2)
        tk.Button(right_frame, text="⏪ Lassítás", command=self.decrease_speed, width=24).pack(pady=2)
        tk.Button(right_frame, text="🔄 Újragenerálás", command=self.reset, width=24).pack(pady=2)

        self.show_sense = tk.BooleanVar(value=False)
        tk.Checkbutton(right_frame, text="Érzékelési sugár (Látótáv)", variable=self.show_sense, bg="#161b22", fg="white", selectcolor="#161b22").pack(pady=2)

        self.show_energy = tk.BooleanVar(value=True)
        tk.Checkbutton(right_frame, text="Energiaszintek", variable=self.show_energy, bg="#161b22", fg="white", selectcolor="#161b22").pack(pady=2)

        tk.Button(right_frame, text="📊 Evolúciós Grafikonok", command=self.open_graph_window, bg="#1f6beb", fg="white", font=("Arial", 9, "bold"), width=22).pack(pady=(10, 15))

        self.create_population()
        self.create_food()
        self.update()

    def on_food_slider_change(self, val):
        self.settings["food_spawn_chance"] = float(val) / 100.0

    def add_instant_food(self):
        for _ in range(30):
            if len(self.foods) < self.settings["max_food"]:
                self.foods.append(Food(self.settings["width"], self.settings["height"]))

    def create_population(self):
        self.bacterias = [
            Bacteria(
                random.uniform(30, self.settings["width"] - 30),
                random.uniform(30, self.settings["height"] - 30),
                self.settings
            ) for _ in range(self.settings["start_bacteria"])
        ]

    def create_food(self):
        self.foods = [Food(self.settings["width"], self.settings["height"]) for _ in range(self.settings["start_food"])]

    def toggle_pause(self):
        self.running = not self.running
        self.pause_button.config(text="⏸ Szünet" if self.running else "▶ Folytatás")
        if self.running:
            self.last_time = time.perf_counter()

    def increase_speed(self):
        self.speed_multiplier = min(self.speed_multiplier * 2, 16)

    def decrease_speed(self):
        self.speed_multiplier = max(self.speed_multiplier / 2, 0.25)

    def reset(self):
        self.generation = 0
        self.total_births = 0
        self.total_deaths = 0
        self.elapsed_time = 0.0
        self.history = {"time": [], "population": [], "speed": [], "size": [], "sense": [], "mating_propensity": [], "efficiency": []}
        Bacteria.next_id = 0
        self.create_population()
        self.create_food()
        self.last_time = time.perf_counter()

    def simulate(self, dt):
        self.elapsed_time += dt

        for food in self.foods:
            food.update(dt)

        if len(self.foods) < self.settings["max_food"]:
            if random.random() < (self.settings["food_spawn_chance"] * dt * 60):
                self.foods.append(Food(self.settings["width"], self.settings["height"]))

        for b in self.bacterias[:]:
            b.move(self.foods, self.bacterias, dt)
            b.eat(self.foods)

        new_bacterias = []
        shuffled = self.bacterias[:]
        random.shuffle(shuffled)
        paired = set()

        for b in shuffled:
            if b.id in paired:
                continue

            for other in shuffled:
                if other is b or other.id in paired:
                    continue
                if b.can_reproduce_with(other):
                    if len(self.bacterias) + len(new_bacterias) < self.settings["max_bacteria"]:
                        baby = b.reproduce_with(other)
                        if baby:
                            new_bacterias.append(baby)
                            paired.add(b.id)
                            paired.add(other.id)
                            self.total_births += 1
                            self.generation = max(self.generation, baby.generation)
                    break

        self.bacterias.extend(new_bacterias)

        survivors = []
        for b in self.bacterias:
            if b.is_dead():
                self.total_deaths += 1
            else:
                survivors.append(b)
        self.bacterias = survivors

        if len(self.bacterias) == 0:
            self.create_population()

    def calculate_statistics(self):
        if not self.bacterias:
            return {"population": 0, "speed": 0, "size": 0, "sense": 0, "mating_propensity": 0, "efficiency": 0}
        c = len(self.bacterias)
        return {
            "population": c,
            "speed": sum(b.speed for b in self.bacterias) / c,
            "size": sum(b.size for b in self.bacterias) / c,
            "sense": sum(b.sense for b in self.bacterias) / c,
            "mating_propensity": sum(b.mating_propensity for b in self.bacterias) / c,
            "efficiency": sum(b.efficiency for b in self.bacterias) / c,
        }

    def update_history(self):
        if not hasattr(self, "_last_hist_save"):
            self._last_hist_save = 0
        if self.elapsed_time - self._last_hist_save >= 0.5:
            self._last_hist_save = self.elapsed_time
            stats = self.calculate_statistics()
            self.history["time"].append(self.elapsed_time)
            for k in ["population", "speed", "size", "sense", "mating_propensity", "efficiency"]:
                self.history[k].append(stats[k])

    def draw(self):
        self.canvas.delete("all")

        # Háttérrács
        for x in range(0, self.settings["width"], 50):
            self.canvas.create_line(x, 0, x, self.settings["height"], fill="#131720")
        for y in range(0, self.settings["height"], 50):
            self.canvas.create_line(0, y, self.settings["width"], y, fill="#131720")

        for food in self.foods:
            food.draw(self.canvas)

        for b in self.bacterias:
            b.draw(self.canvas, self.show_sense.get(), self.show_energy.get())

        stats = self.calculate_statistics()
        text = (
            f"POPULÁCIÓ: {stats['population']} / {self.settings['max_bacteria']}\n"
            f"ÉTEL:      {len(self.foods)} / {self.settings['max_food']}\n"
            f"GENERÁCIÓ: {self.generation}\n"
            f"IDŐ:       {int(self.elapsed_time)} mp\n\n"
            f"ÁTLAGOS FENOTÍPUS / GÉNEK:\n"
            f"  Sebesség:          {stats['speed']:.2f}\n"
            f"  Méret:             {stats['size']:.2f}\n"
            f"  Látótávolság:      {stats['sense']:.1f}\n"
            f"  Párosodási hajlam: {stats['mating_propensity']*100:.1f}%\n"
            f"  Emésztési haték.:  {stats['efficiency']*100:.1f}%\n\n"
            f"STATISZTIKA:\n"
            f"  Születések:  {self.total_births}\n"
            f"  Halálozások: {self.total_deaths}"
        )
        self.stats_label.config(text=text)

    def open_graph_window(self):
        g_win = tk.Toplevel(self.root)
        g_win.title("Gének fejlődése (Kezdettől fogva)")
        g_win.geometry("900x750")
        g_win.configure(bg="#0d1117")

        canvas = tk.Canvas(g_win, bg="#0d1117", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)

        def draw_graphs():
            if not g_win.winfo_exists():
                return
            canvas.delete("all")

            times = self.history["time"]
            if len(times) < 2:
                canvas.create_text(450, 350, text="Adatgyűjtés folyamatban...", fill="white", font=("Arial", 14))
                g_win.after(500, draw_graphs)
                return

            graphs = [
                ("Populáció Nagysága", self.history["population"], "#58a6ff"),
                ("Sebesség Gén", self.history["speed"], "#f0883e"),
                ("Méret Gén", self.history["size"], "#ff7b72"),
                ("Látótávolság Gén (Sense)", self.history["sense"], "#3fb950"),
                ("Párosodási Hajlam", self.history["mating_propensity"], "#d2a8ff"),
                ("Emésztési Hatékonyság", self.history["efficiency"], "#f1e05a"),
            ]

            w = canvas.winfo_width()
            h = canvas.winfo_height()
            g_h = (h - 40) / len(graphs)
            t_min, t_max = times[0], times[-1]

            for index, (title, values, color) in enumerate(graphs):
                top = 20 + index * g_h
                bottom = top + g_h - 22
                left, right = 110, w - 30

                canvas.create_rectangle(left, top, right, bottom, outline="#30363d", fill="#161b22")
                canvas.create_text(10, top + 8, text=title, fill="white", anchor="w", font=("Arial", 8, "bold"))

                v_min, v_max = min(values), max(values)
                if v_min == v_max:
                    v_max += 0.1

                canvas.create_text(left - 5, top + 5, text=f"{v_max:.2f}", fill="#8b949e", anchor="e", font=("Arial", 7))
                canvas.create_text(left - 5, bottom - 5, text=f"{v_min:.2f}", fill="#8b949e", anchor="e", font=("Arial", 7))

                points = []
                for i in range(len(times)):
                    x = left + ((times[i] - t_min) / max(t_max - t_min, 0.001)) * (right - left)
                    y = bottom - ((values[i] - v_min) / (v_max - v_min)) * (bottom - top)
                    points.extend([x, y])

                if len(points) >= 4:
                    canvas.create_line(*points, fill=color, width=2)

                canvas.create_text(right, top - 6, text=f"Jelenlegi: {values[-1]:.2f}", fill=color, anchor="e", font=("Arial", 8, "bold"))

            canvas.create_text(left, h - 8, text="0 mp (Kezdet)", fill="#8b949e", anchor="w", font=("Arial", 8))
            canvas.create_text(right, h - 8, text=f"{int(t_max)} mp (Jelen)", fill="#8b949e", anchor="e", font=("Arial", 8))

            g_win.after(500, draw_graphs)

        draw_graphs()

    def update(self):
        now = time.perf_counter()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now

        if self.running:
            dt *= self.speed_multiplier
            self.simulate(dt)
            self.update_history()

        self.draw()
        self.root.after(16, self.update)


# ============================================================
# INDÍTÁS
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = Simulation(root)
    root.mainloop()