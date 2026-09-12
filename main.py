import tkinter as tk
from tkinter import messagebox
import math


class RotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Аффинные преобразования: Поворот")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)

        # Начальные и текущие декартовы координаты треугольника (A, B, C)
        self.o_v = [-50, -50, -50, 100, 100, -50]
        self.ax, self.ay, self.bx, self.by, self.cx, self.cy = self.o_v

        # Точка поворота O'
        self.center_x, self.center_y = 50, 50
        self.w, self.h = 650, 650
        self.scale = 1.0

        # Смещение самого холста (для перемещения зажимом ЛКМ)
        self.pan_x, self.pan_y = 0.0, 0.0

        self.setup_ui()
        self.draw_scene()

    def setup_ui(self):
        f = tk.LabelFrame(self.root, text=" Управление ", padx=10, pady=10, bg="#f8f9fa")
        f.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        tk.Label(f, text="Координаты вершин:", font=("Arial", 10, "bold"), bg="#f8f9fa").pack(anchor=tk.W)
        vf = tk.Frame(f, bg="#f8f9fa");
        vf.pack(anchor=tk.W, pady=5)

        self.ents = []
        labels = [("A X:", "-50"), ("Y:", "-50"), ("B X:", "-50"), ("Y:", "100"), ("C X:", "100"), ("Y:", "-50")]
        for i, (txt, val) in enumerate(labels):
            tk.Label(vf, text=txt, bg="#f8f9fa").grid(row=i // 2, column=(i % 2) * 2)
            e = tk.Entry(vf, width=5);
            e.insert(0, val);
            e.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=2, pady=2)
            self.ents.append(e)

        tk.Button(f, text="Обновить объект", bg="#f8f9fa", command=self.update_v).pack(fill=tk.X, pady=5)
        tk.Frame(f, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=10)

        tk.Label(f, text="Точка поворота (X,Y):", font=("Arial", 10, "bold"), bg="#f8f9fa").pack(anchor=tk.W)
        cf = tk.Frame(f, bg="#f8f9fa");
        cf.pack(anchor=tk.W, pady=5)
        self.e_cx = tk.Entry(cf, width=5);
        self.e_cx.insert(0, "50");
        self.e_cx.grid(row=0, column=0, padx=2)
        self.e_cy = tk.Entry(cf, width=5);
        self.e_cy.insert(0, "50");
        self.e_cy.grid(row=0, column=1, padx=2)
        tk.Button(f, text="Применить", command=self.update_c).pack(fill=tk.X, pady=5)

        tk.Frame(f, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=10)
        tk.Label(f, text="Угол (градусы):", font=("Arial", 10, "bold"), bg="#f8f9fa").pack(anchor=tk.W)
        self.e_ang = tk.Entry(f, width=10);
        self.e_ang.insert(0, "45");
        self.e_ang.pack(anchor=tk.W, pady=5)

        tk.Button(f, text="Повернуть", bg="#f8f9fa",  font=("Arial", 10, "bold"), command=self.rotate).pack(
            fill=tk.X, pady=5)
        tk.Button(f, text="Сбросить", bg="#f8f9fa",  command=self.reset).pack(fill=tk.X, pady=5)


        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h, bg="white", highlightthickness=1,
                                highlightbackground="gray")
        self.canvas.pack(side=tk.RIGHT, padx=15, pady=15)

        # События мыши для перемещения холста, кликов и зума
        self.canvas.bind("<Button-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.do_pan)
        self.canvas.bind("<Button-3>", self.click_c)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-4>", self.zoom)
        self.canvas.bind("<Button-5>", self.zoom)

    def to_c(self, x, y):
        """Перевод математических координат в пиксели холста (с учетом зума и сдвига панорамирования)."""
        mid_x = (self.w / 2) + self.pan_x
        mid_y = (self.h / 2) + self.pan_y
        return mid_x + (x * self.scale), mid_y - (y * self.scale)

    def to_m(self, cx, cy):
        """Перевод пикселей холста обратно в математические декартовы координаты."""
        mid_x = (self.w / 2) + self.pan_x
        mid_y = (self.h / 2) + self.pan_y
        return (cx - mid_x) / self.scale, (mid_y - cy) / self.scale

    def start_pan(self, event):
        """Запоминаем начальную точку нажатия ЛКМ для перемещения холста."""
        self.mouse_start_x = event.x
        self.mouse_start_y = event.y

    def do_pan(self, event):
        """Вычисляем разницу смещения при движении мыши с зажатой ЛКМ."""
        dx = event.x - self.mouse_start_x
        dy = event.y - self.mouse_start_y
        self.pan_x += dx
        self.pan_y += dy
        self.mouse_start_x = event.x
        self.mouse_start_y = event.y
        self.draw_scene()

    def draw_scene(self):
        self.canvas.delete("all")
        mid_x = (self.w / 2) + self.pan_x
        mid_y = (self.h / 2) + self.pan_y
        step = 100 if self.scale < 0.4 else (20 if self.scale > 2.5 else 50)

        # Отрисовка динамической координатной сетки
        max_range = int(max(self.w, self.h) / self.scale) + int(
            max(abs(self.pan_x), abs(self.pan_y)) / self.scale) + step
        for i in range(step, max_range, step):
            for sign in [1, -1]:
                val = i * sign
                lx, ly = self.to_c(val, val)
                if 0 <= lx <= self.w:
                    self.canvas.create_line(lx, 0, lx, self.h, fill="#f4f4f4")
                    self.canvas.create_text(lx, mid_y + 12, text=str(val), fill="gray", font=("Arial", 7))
                if 0 <= ly <= self.h:
                    self.canvas.create_line(0, ly, self.w, ly, fill="#f4f4f4")
                    self.canvas.create_text(mid_x - 15, ly, text=str(val), fill="gray", font=("Arial", 7))

        # Главные математические оси X и Y, привязанные к центру сдвига
        self.canvas.create_line(0, mid_y, self.w, mid_y, fill="black", width=2, arrow=tk.LAST)
        self.canvas.create_text(self.w - 15, mid_y + 15, text="X", font=("Arial", 11, "bold"))
        self.canvas.create_line(mid_x, self.h, mid_x, 0, fill="black", width=2, arrow=tk.LAST)
        self.canvas.create_text(mid_x - 15, 15, text="Y", font=("Arial", 11, "bold"))
        self.canvas.create_text(mid_x - 10, mid_y + 10, text="0", font=("Arial", 9, "bold"))

        # 1. Переводим начальные (оригинальные) координаты в координаты экрана
        orig_ax, orig_ay = self.to_c(self.o_v[0], self.o_v[1])
        orig_bx, orig_by = self.to_c(self.o_v[2], self.o_v[3])
        orig_cx, orig_cy = self.to_c(self.o_v[4], self.o_v[5])

        # 2. Отрисовываем начальное положение пунктиром
        # fill="" означает, что внутри фигура будет прозрачной
        # dash=(4, 4) задает длину штриха и пробела в пикселях
        self.canvas.create_polygon(
            orig_ax, orig_ay, orig_bx, orig_by, orig_cx, orig_cy,
            fill="", outline="red", width=2, dash=(10, 4)
        )

        # Координаты треугольника на холсте
        ax, ay = self.to_c(self.ax, self.ay)
        bx, by = self.to_c(self.bx, self.by)
        cx, cy = self.to_c(self.cx, self.cy)
        self.canvas.create_polygon(ax, ay, bx, by, cx, cy, fill="#e8eaf6", outline="#1a237e", width=2)

        for tx, ty, name, rx, ry in [(ax, ay, "A", self.ax, self.ay), (bx, by, "B", self.bx, self.by),
                                     (cx, cy, "C", self.cx, self.cy)]:
            self.canvas.create_text(tx, ty - 12, text=f"{name}({int(round(rx))},{int(round(ry))})",
                                    font=("Arial", 8, "bold"), fill="#1a237e")

        # Аккуратная тонкая точка поворота O'
        ccx, ccy = self.to_c(self.center_x, self.center_y)
        self.canvas.create_oval(ccx - 3, ccy - 3, ccx + 3, ccy + 3, fill="red", outline="black")
        self.canvas.create_line(ccx - 10, ccy, ccx + 10, ccy, fill="red", width=1)
        self.canvas.create_line(ccx, ccy - 10, ccx, ccy + 10, fill="red", width=1)
        self.canvas.create_text(ccx + 25, ccy - 12, text=f"O'({int(round(self.center_x))},{int(round(self.center_y))})",
                                fill="red", font=("Arial", 9, "bold"))

    def zoom(self, event):
        self.scale *= 1.1 if (event.num == 4 or event.delta > 0) else (1.0 / 1.1)
        self.scale = max(0.15, min(self.scale, 8.0))
        self.draw_scene()

    def update_v(self):
        try:
            self.o_v = [float(e.get()) for e in self.ents]
            self.reset()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числа!")

    def update_c(self):
        try:
            self.center_x, self.center_y = float(self.e_cx.get()), float(self.e_cy.get())
            self.draw_scene()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числа!")

    def click_c(self, event):
        x, y = self.to_m(event.x, event.y)
        self.center_x, self.center_y = x, y
        for e, val in [(self.e_cx, x), (self.e_cy, y)]:
            e.delete(0, tk.END);
            e.insert(0, str(int(round(val))))
        self.draw_scene()

    def rotate(self):
        try:
            rad = math.radians(float(self.e_ang.get()))
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный угол!"); return

        c, s = math.cos(rad), math.sin(rad)
        x0, y0 = self.center_x, self.center_y

        self.ax, self.ay = (self.ax - x0) * c - (self.ay - y0) * s + x0, (self.ax - x0) * s + (self.ay - y0) * c + y0
        self.bx, self.by = (self.bx - x0) * c - (self.by - y0) * s + x0, (self.bx - x0) * s + (self.by - y0) * c + y0
        self.cx, self.cy = (self.cx - x0) * c - (self.cy - y0) * s + x0, (self.cx - x0) * s + (self.cy - y0) * c + y0
        self.draw_scene()

    def reset(self):
        self.ax, self.ay, self.bx, self.by, self.cx, self.cy = self.o_v
        self.pan_x, self.pan_y = 0.0, 0.0  # Сброс сдвига экрана
        self.draw_scene()


if __name__ == "__main__":
    root = tk.Tk()
    app = RotationApp(root)
    root.mainloop()
