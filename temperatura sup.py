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
ruta = r"C:/Users/Mariano/Desktop/siinoptica/mapas sinopticos"

# =========================
# ABRIR DATASET
# =========================
ds = xr.open_dataset(os.path.join(ruta, "tem2025.nc"))

# =========================
# VARIABLE TEMPERATURA
# =========================
temp = ds["t"]

# =========================
# CONVERTIR TIEMPO
# =========================
temp["valid_time"] = pd.to_datetime(temp["valid_time"].values)

# =========================
# FECHA
# =========================
fecha_objetivo = np.datetime64("2025-01-10T12:00")

# =========================
# SELECCIÓN (SIN NIVEL)
# =========================
temp_sel = temp.sel(valid_time=fecha_objetivo).squeeze()

# =========================
# CONVERTIR K → °C
# =========================
temp_sel = temp_sel - 273.15

# =========================
# AJUSTAR LONGITUD
# =========================
if temp_sel.longitude.max() > 180:
    temp_sel = temp_sel.assign_coords(
        longitude=((temp_sel.longitude + 180) % 360 - 180)
    ).sortby("longitude")

# =========================
# RECORTE SUDAMÉRICA
# =========================
temp_sel = temp_sel.sel(
    latitude=slice(15, -60),
    longitude=slice(-90, -30)
)

# =========================
# CONFIGURACIÓN GRÁFICA
# =========================
niveles = np.arange(0, 45, 2)
cmap = "turbo"

# =========================
# MAPA
# =========================
fig = plt.figure(figsize=(11, 6), dpi=180)
ax = plt.axes(projection=ccrs.PlateCarree())

pcm = ax.contourf(
    temp_sel.longitude,
    temp_sel.latitude,
    temp_sel,
    levels=niveles,
    cmap=cmap,
    extend="both",
    transform=ccrs.PlateCarree()
)

# Isotermas (opcional pero recomendable)
cont = ax.contour(
    temp_sel.longitude,
    temp_sel.latitude,
    temp_sel,
    levels=np.arange(0, 45, 5),
    colors="black",
    linewidths=0.6,
    transform=ccrs.PlateCarree()
)

ax.clabel(cont, fmt="%d", fontsize=6)

# =========================
# MAPA BASE
# =========================
ax.coastlines("10m", linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linewidth=0.6)
ax.add_feature(cfeature.RIVERS, linewidth=0.4)

gl = ax.gridlines(draw_labels=True, linewidth=0.3, linestyle="--")
gl.top_labels = False
gl.right_labels = False

# =========================
# COLORBAR
# =========================
cbar = plt.colorbar(
    pcm,
    orientation="horizontal",
    pad=0.09,
    aspect=70,
    shrink=0.5
)

cbar.set_label("Temperatura superficial (°C)", fontsize=8)

# =========================
# TÍTULO
# =========================
ax.set_title(
    "Temperatura superficial\n10 de enero de 2025 – 12:00 UTC",
    fontsize=8
)

plt.tight_layout()
plt.show()
