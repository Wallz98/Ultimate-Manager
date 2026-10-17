import flet as ft
import flet.canvas as cv

# Tamanho padrão de exibição (px)
LARGURA = 150
ALTURA = 173

# Espaço base de desenho
_BASE_W, _BASE_H = 100, 115

_METADES = {
    "Clássico": [
        ("M", 50, 4), ("L", 84, 4), ("Q", 84, 16, 96, 20),
        ("L", 96, 55), ("C", 96, 85, 72, 100, 50, 114),
    ],
    "Curvo": [
        ("M", 50, 8), ("Q", 75, 9, 95, 4),
        ("L", 95, 45), ("C", 95, 78, 72, 100, 50, 114),
    ],
    "Pontudo": [
        ("M", 50, 2), ("Q", 75, 10, 96, 8),
        ("L", 96, 50), ("C", 96, 80, 72, 100, 50, 114),
    ],
    "Ornamentado": [
        ("M", 50, 2), ("Q", 72, 6, 82, 14), ("Q", 82, 26, 96, 32),
        ("L", 96, 50), ("C", 96, 80, 72, 100, 50, 114),
    ],
    "Inclinado": [
        ("M", 50, 4), ("Q", 75, 6, 96, 12),
        ("L", 96, 50), ("C", 96, 82, 70, 100, 50, 114),
    ],
    "Côncavo": [
        ("M", 50, 14), ("Q", 62, 14, 72, 6), ("L", 96, 16),
        ("L", 96, 52), ("C", 96, 82, 72, 100, 50, 114),
    ],
    "Heráldico": [
        ("M", 50, 2), ("Q", 75, 2, 96, 10),
        ("L", 96, 70), ("L", 50, 114),
    ],
    "Largo": [
        ("M", 50, 4), ("Q", 78, 4, 96, 8),
        ("L", 96, 70), ("Q", 94, 86, 80, 94), ("L", 50, 114),
    ],
    "Entalhado": [
        ("M", 50, 4), ("Q", 75, 4, 96, 10),
        ("L", 96, 42), ("Q", 88, 56, 96, 70),
        ("L", 96, 82), ("Q", 90, 100, 50, 114),
    ],
}

FORMATOS = list(_METADES.keys())


def _amostrar(cmds, passos=16):
    pts, atual = [], None
    for c in cmds:
        t = c[0]
        if t in ("M", "L"):
            atual = (c[1], c[2])
            pts.append(atual)
        elif t == "Q":
            x0, y0 = atual
            cx, cy, x, y = c[1:]
            for i in range(1, passos + 1):
                u = i / passos
                px = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u ** 2 * x
                py = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u ** 2 * y
                pts.append((px, py))
            atual = (x, y)
        elif t == "C":
            x0, y0 = atual
            c1x, c1y, c2x, c2y, x, y = c[1:]
            for i in range(1, passos + 1):
                u = i / passos
                a, b, d, e = (1 - u) ** 3, 3 * (1 - u) ** 2 * \
                    u, 3 * (1 - u) * u ** 2, u ** 3
                pts.append((a * x0 + b * c1x + d * c2x + e * x,
                            a * y0 + b * c1y + d * c2y + e * y))
                atual = (x, y)
    return pts


def _contorno(nome):
    direita = _amostrar(_METADES.get(nome, _METADES["Clássico"]))
    esquerda = [(_BASE_W - x, y) for x, y in reversed(direita[1:-1])]
    return direita + esquerda


def _escalar(pts, fator, cx=50, cy=57):
    return [(cx + (x - cx) * fator, cy + (y - cy) * fator) for x, y in pts]


def _recortar_x(pts, xmin=None, xmax=None):
    def recortar(poli, dentro, inter):
        saida = []
        for i in range(len(poli)):
            a, b = poli[i - 1], poli[i]
            if dentro(b):
                if not dentro(a):
                    saida.append(inter(a, b))
                saida.append(b)
            elif dentro(a):
                saida.append(inter(a, b))
        return saida

    def interx(x):
        return lambda a, b: (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))

    if xmin is not None:
        pts = recortar(pts, lambda p: p[0] >= xmin, interx(xmin))
    if xmax is not None and pts:
        pts = recortar(pts, lambda p: p[0] <= xmax, interx(xmax))
    return pts


def _path(pts, cor, largura=LARGURA, altura=ALTURA):
    if len(pts) < 3:
        return None
    sx, sy = largura / _BASE_W, altura / _BASE_H
    elementos = [cv.Path.MoveTo(pts[0][0] * sx, pts[0][1] * sy)]
    elementos += [cv.Path.LineTo(x * sx, y * sy) for x, y in pts[1:]]
    elementos.append(cv.Path.Close())
    return cv.Path(
        elementos,
        paint=ft.Paint(color=cor, style=ft.PaintingStyle.FILL,
                       anti_alias=True),
    )


def gerar_escudo(formato, cor_fundo, cor_listras, cor_borda, brilho=True, largura=LARGURA, altura=ALTURA):
    externo = _contorno(formato)
    interno = _escalar(externo, 0.89)

    shapes = [
        _path(externo, cor_borda, largura, altura),
        _path(interno, cor_fundo, largura, altura)
    ]

    largura_listra = 14
    for centro in (24, 50, 76):
        faixa = _recortar_x(interno, centro - largura_listra /
                            2, centro + largura_listra / 2)
        shapes.append(_path(faixa, cor_listras, largura, altura))

    if brilho:
        metade = _recortar_x(interno, xmin=50)
        shapes.append(_path(metade, ft.Colors.with_opacity(
            0.18, ft.Colors.BLACK), largura, altura))

    return [s for s in shapes if s is not None]


def criar_widget_escudo(formato="Clássico", simbolo="Bola", c1="Azul", c2="Vermelho", c3="Amarelo", c4="Branco", largura=140, **kwargs):
    import gerador

    fmt = kwargs.get('escudo_formato', kwargs.get('formato', formato))
    if fmt not in FORMATOS:
        fmt = "Clássico"

    simb = kwargs.get('icone', kwargs.get('simbolo_escudo', kwargs.get(
        'simbolo_time', kwargs.get('simbolo', simbolo))))
    if not simb or simb not in gerador.ICONES:
        simb = "Bola"

    cor1 = gerador.obter_cor_flet(kwargs.get('cor_1', kwargs.get('c1', c1)))
    cor2 = gerador.obter_cor_flet(kwargs.get('cor_2', kwargs.get('c2', c2)))
    cor3 = gerador.obter_cor_flet(kwargs.get('cor_3', kwargs.get('c3', c3)))
    cor4 = gerador.obter_cor_flet(kwargs.get('cor_4', kwargs.get('c4', c4)))

    altura = largura * (115.0 / 100.0)
    sx = largura / 100.0

    shapes = gerar_escudo(fmt, cor1, cor2, cor3,
                          largura=largura, altura=altura)
    canvas_escudo = cv.Canvas(shapes=shapes, width=largura, height=altura)

    icone_nome = gerador.ICONES.get(simb, ft.Icons.SPORTS_SOCCER)
    icone_size = max(10, 36 * sx)
    pad_bottom = 14 * sx

    return ft.Container(
        width=largura,
        height=altura,
        alignment=ft.alignment.center,
        content=ft.Stack([
            canvas_escudo,
            ft.Container(
                content=ft.Icon(name=icone_nome, size=icone_size, color=cor4),
                width=largura,
                height=altura,
                alignment=ft.alignment.center,
                padding=ft.padding.only(bottom=pad_bottom)
            )
        ])
    )
