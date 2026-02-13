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
# RUTA DE ARCHIVOS
# =========================
ruta = r"C:/Users/Mariano/Desktop/siinoptica/mapas sinopticos"

# =========================
# ABRIR DATASETS
# =========================
ds_hr = xr.open_dataset(os.path.join(ruta, "HR2025.nc"))
ds_u  = xr.open_dataset(os.path.join(ruta, "uwnd2025.nc"))
ds_v  = xr.open_dataset(os.path.join(ruta, "vwnd2025.nc"))

# =========================
# CONVERTIR TIEMPO A DATETIME
# =========================
ds_hr["valid_time"] = pd.to_datetime(ds_hr["valid_time"].values)
ds_u["time"] = pd.to_datetime(ds_u["time"].values)
ds_v["time"] = pd.to_datetime(ds_v["time"].values)

# =========================
# FECHA Y NIVEL
# =========================
fecha = np.datetime64("2025-01-13T12:00")
nivel = 850

# =========================
# SELECCIÓN
# =========================
hr = ds_hr["r"].sel(valid_time=fecha, pressure_level=nivel).squeeze()
u  = ds_u["uwnd"].sel(time=fecha, level=nivel).squeeze()
v  = ds_v["vwnd"].sel(time=fecha, level=nivel).squeeze()

# =========================
# AJUSTE LONGITUD
# =========================
def ajustar_longitud(da, lon_name):
    if float(da[lon_name].max()) > 180:
        da = da.assign_coords(
            {lon_name: (((da[lon_name] + 180) % 360) - 180)}
        ).sortby(lon_name)
    return da

hr = ajustar_longitud(hr, "longitude")
u  = ajustar_longitud(u, "lon")
v  = ajustar_longitud(v, "lon")

# =========================
# RECORTE
# =========================
hr = hr.sel(latitude=slice(15, -60), longitude=slice(-90, -30))
u  = u.sel(lat=slice(15, -60), lon=slice(-90, -30))
v  = v.sel(lat=slice(15, -60), lon=slice(-90, -30))

# =========================
# FIGURA
# =========================
fig = plt.figure(figsize=(11, 7), dpi=180)
ax = plt.axes(projection=ccrs.PlateCarree())

# =========================
# HUMEDAD RELATIVA
# =========================
niveles = np.arange(0, 105, 5)

pcm = ax.contourf(
    hr.longitude,
    hr.latitude,
    hr.values,
    levels=niveles,
    cmap="BrBG",
    extend="both",
    alpha=0.6,
    transform=ccrs.PlateCarree()
)

# =========================
# VIENTO
# =========================
skip = 1
lon2d, lat2d = np.meshgrid(u.lon.values, u.lat.values)

magnitud = np.sqrt(u.values**2 + v.values**2)
max_vel = np.max(magnitud)
vel_prom = np.mean(magnitud)

Q = ax.quiver(
    lon2d[::skip, ::skip],
    lat2d[::skip, ::skip],
    u.values[::skip, ::skip],
    v.values[::skip, ::skip],
    color="red",
    scale=max_vel * 5,
    width=0.004,
    headlength=5,
    headaxislength=3.5,
    transform=ccrs.PlateCarree()
)

# =========================
# MAPA BASE
# =========================
ax.coastlines("10m", linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linewidth=0.6)

gl = ax.gridlines(draw_labels=True, linestyle="--", linewidth=0.3)
gl.top_labels = False
gl.right_labels = False

# =========================
# COLORBAR
# =========================
cbar = plt.colorbar(
    pcm,
    orientation="horizontal",
    pad=0.08,
    aspect=70,
    shrink=0.5
)
cbar.set_label("Humedad Relativa (%)", fontsize=8)

# =========================
# FLECHA DE REFERENCIA (ABAJO)
# =========================
ax.quiverkey(
    Q,
    X=1,              # centrado horizontalmente
    Y=-0.07,            # debajo del mapa, arriba de la barra
    U=float(f"{vel_prom:.2f}"),
    label=f"{vel_prom:.2f} m/s",
    labelpos="E",
    coordinates="axes",
    fontproperties={'size': 5}   # texto más pequeño
)

# =========================
# TÍTULO
# =========================
ax.set_title(
    "Humedad Relativa (%) y Viento a 850 hPa\n13 Enero 2025 – 12:00 UTC",
    fontsize=8
)

plt.tight_layout()
plt.show()



