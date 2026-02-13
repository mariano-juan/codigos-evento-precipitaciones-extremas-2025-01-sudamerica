# =========================
# LIBRERÍAS
# =========================
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import os

# =========================
# RUTA
# =========================
ruta = "C:/Users/Mariano/Desktop/siinoptica/mapas sinopticos"

# =========================
# ABRIR DATASET
# =========================
ds = xr.open_dataset(os.path.join(ruta, "div2025.nc"))

# =========================
# VARIABLE DE DIVERGENCIA
# =========================
div = ds["d"]

# =========================
# ASEGURAR FORMATO DE TIEMPO
# =========================
div["valid_time"] = pd.to_datetime(div["valid_time"].values)

# =========================
# SELECCIÓN FECHA Y NIVEL
# =========================
div = div.sel(
    valid_time=np.datetime64("2025-07-15T12:00"),
    pressure_level=200
)

# =========================
# AJUSTE DE LONGITUD (0–360 → -180–180)
# =========================
if div.longitude.max() > 180:
    div = div.assign_coords(
        longitude=(((div.longitude + 180) % 360) - 180)
    ).sortby("longitude")

# =========================
# DOMINIO SUDAMÉRICA
# =========================
div = div.sel(
    latitude=slice(15, -60),
    longitude=slice(-90, -30)
)

# =========================
# CONFIGURACIÓN GRÁFICA
# =========================
# Valores típicos en 200 hPa
niveles = np.linspace(-5e-5, 5e-5, 21)
cmap = plt.cm.RdBu_r

# =========================
# MAPA
# =========================
fig = plt.figure(figsize=(11, 6), dpi=180)
ax = plt.axes(projection=ccrs.PlateCarree())

pcm = ax.contourf(
    div.longitude,
    div.latitude,
    div,
    levels=niveles,
    cmap=cmap,
    extend="both",
    transform=ccrs.PlateCarree()
)

# MAPA BASE
ax.coastlines("10m", linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linewidth=0.6)
ax.add_feature(cfeature.RIVERS, linewidth=0.4)

gl = ax.gridlines(draw_labels=True, linewidth=0.3, linestyle="--")
gl.top_labels = False
gl.right_labels = False

# COLORBAR
cbar = plt.colorbar(
    pcm,
    orientation="horizontal",
    pad=0.06,
    aspect=40
)
cbar.set_label("Divergencia (s⁻¹)", fontsize=11)

# TÍTULO
ax.set_title(
    "Divergencia a 200 hPa\n15 de julio de 2025 – 12:00 UTC",
    fontsize=13
)

plt.show()
