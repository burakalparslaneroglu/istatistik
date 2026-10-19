"""Konu 5: aynı moment tanımından uygulama, Python ve temel R hesapları."""

from core.labs import expr as E
from core.labs.spec import Derive, Scalar, Statistic


MOMENT_LABELS = {
    "bicim_m2": "İkinci merkezî moment m₂",
    "bicim_m3": "Üçüncü merkezî moment m₃",
    "bicim_m4": "Dördüncü merkezî moment m₄",
    "bicim_g1": "Çarpıklık g₁",
    "bicim_b2": "Basıklık b₂",
    "bicim_g2": "Fazla basıklık g₂",
}


def moment_operations(frame, deviation, square, cube, fourth, digits=None, *, signless=False):
    """Sapmalar daha önce türetilmiştir; momentlerin paydası n'dir (n−1 değildir).

    Sabit veri bu işlemlere gönderilmez: m₂=0 için standartlaştırılmış katsayılar tanımsızdır.
    Yanlılık düzeltmesi veya paketlerin farklı skew/kurtosis varsayılanları kullanılmaz.
    """
    digits = dict.fromkeys(MOMENT_LABELS, 3) | (digits or {})
    return (
        Derive(frame, cube, E.power(E.var(deviation), 3), "Küplü sapma (xᵢ − x̄)³"),
        Derive(frame, fourth, E.power(E.var(deviation), 4), "Dördüncü kuvvetli sapma (xᵢ − x̄)⁴"),
        *(Statistic(frame, column, "mean", name, MOMENT_LABELS[name], decimals=digits[name])
          for column, name in ((square, "bicim_m2"), (cube, "bicim_m3"), (fourth, "bicim_m4"))),
        Scalar("bicim_g1", E.div(E.ref("bicim_m3"), E.power(E.ref("bicim_m2"), 1.5)),
               MOMENT_LABELS["bicim_g1"], decimals=digits["bicim_g1"], signless=signless),
        Scalar("bicim_b2", E.div(E.ref("bicim_m4"), E.power(E.ref("bicim_m2"), 2)),
               MOMENT_LABELS["bicim_b2"], decimals=digits["bicim_b2"], signless=signless),
        Scalar("bicim_g2", E.sub(E.ref("bicim_b2"), 3), MOMENT_LABELS["bicim_g2"],
               decimals=digits["bicim_g2"], signless=signless),
    )
