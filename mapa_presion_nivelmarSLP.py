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
import matplotlib.ticker as mticker

# =========================
# RUTA
# =========================
ruta = "C:/Users/Mariano/Desktop/siinoptica/mapas sinopticos"

# =========================
# ABRIR DATASET
# =========================
ds = xr.open_dataset(os.path.join(ruta, "slp2025.nc"))

# =========================
# VARIABLE (SLP)
# =========================
slp = ds["slp"]

# =========================
# ASEGURAR FORMATO DE TIEMPO
# =========================
slp["time"] = pd.to_datetime(slp["time"].values)

# =========================
# SELECCIÓN DE FECHA
# =========================
fecha_objetivo = np.datetime64("2025-01-06T12:00")
slp = slp.sel(time=fecha_objetivo)

# =========================
# CONVERTIR A hPa (si está en Pa)
# =========================
if float(slp.max()) > 2000:
    slp = slp / 100.0

# =========================
# AJUSTE DE LONGITUD (0–360 → -180–180)
# =========================
if float(slp.lon.max()) > 180:
    slp = slp.assign_coords(
        lon=(((slp.lon + 180) % 360) - 180)
    ).sortby("lon")

# =========================
# DOMINIO SUDAMÉRICA
# =========================
slp = slp.sel(
    lat=slice(15, -60),
    lon=slice(-90, -30)
)

# =========================
# CONFIGURACIÓN GRÁFICA
# =========================
niveles_relleno = np.arange(980, 1040, 4)
niveles_isobaras = np.arange(980, 1040, 8)

# =========================
# MAPA
# =========================
fig = plt.figure(figsize=(14, 7), dpi=180)
ax = plt.axes(projection=ccrs.PlateCarree())

# Campo relleno
pcm = ax.contourf(
    slp.lon,
    slp.lat,
    slp,
    levels=niveles_relleno,
    cmap="viridis",
    extend="both",
    transform=ccrs.PlateCarree()
)

# Isobaras
contornos = ax.contour(
    slp.lon,
    slp.lat,
    slp,
    levels=niveles_isobaras,
    colors="black",
    linewidths=1.2,
    transform=ccrs.PlateCarree()
)

ax.clabel(contornos, fmt="%d", fontsize=9)

# =========================
# MAPA BASE
# =========================
ax.coastlines("10m", linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linewidth=0.6)
ax.add_feature(cfeature.RIVERS, linewidth=0.4)

# =========================
# GRIDLINES CADA 10°
# =========================
gl = ax.gridlines(draw_labels=True, linewidth=0.3, linestyle="--")

gl.top_labels = False
gl.right_labels = False

gl.xlocator = mticker.FixedLocator(np.arange(-90, -29, 10))
gl.ylocator = mticker.FixedLocator(np.arange(-60, 16, 10))

# =========================
# COLORBAR MÁS FINA
# =========================
cbar = plt.colorbar(
    pcm,
    orientation="horizontal",
    pad=0.09,
    aspect=70,
    shrink=0.5
)

cbar.set_label("Presión a nivel del mar (hPa)", fontsize=9)

# =========================
# TÍTULO
# =========================
ax.set_title(
    "Presión a nivel del mar (MSLP)\n06 de enero de 2025 – 12:00 UTC",
    fontsize=8
)

plt.tight_layout()
plt.show()

