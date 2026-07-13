from pathlib import Path

cwd = Path.cwd()
input_dir = cwd / "input"
agro_dir = input_dir / "agro"
agro_fp = agro_dir / "agro.yaml"
crop_dir = input_dir / "crop"
crop_fp = crop_dir / "springwheat.yaml"
modelconf_dir = input_dir / "modelconf"
modelconf_fp = modelconf_dir / "lintul3.conf"
site_dir = input_dir / "site"
site_fp = site_dir / "site.yaml"
soil_dir = input_dir / "soil"
soil_fp = soil_dir / "soil.yaml"
weather_dir = input_dir / "weather"
weather_fn= weather_dir / "NLD1"