from pcse.base import ParameterProvider
from pcse.engine import Engine
from pcse.input import CABOWeatherDataProvider
import input_file_paths as ifp
import matplotlib.pyplot as plt
import output_file_paths as ofp
import pandas as pd
import yaml

def run_model_and_collect_output(agrod, parameters, wdp, modelconf_fp):
    model = Engine(parameters, wdp, agrod, config=modelconf_fp)
    model.run_till_terminate()
    output = model.get_output()
    df_out = pd.DataFrame(output)
    return df_out

def main():
    with open(ifp.crop_fp) as f:
        cropd = yaml.safe_load(f.read())
    with open(ifp.agro_fp) as f:
        agrod = yaml.safe_load(f.read())
    with open(ifp.soil_fp) as f:
        soild = yaml.safe_load(f.read())
    with open(ifp.site_fp) as f:
        sited = yaml.safe_load(f.read())
    wdp = CABOWeatherDataProvider(fname=ifp.weather_fn, fpath=ifp.weather_dir)
    parameters = ParameterProvider(cropdata=cropd,
                                   sitedata=sited,
                                   soildata=soild)

    df_out_pp = run_model_and_collect_output(agrod, parameters, wdp, ifp.modelconf_pp_fp)
    df_out_wlp = run_model_and_collect_output(agrod, parameters, wdp, ifp.modelconf_wlp_fp)
    df_out_wnlp = run_model_and_collect_output(agrod, parameters, wdp, ifp.modelconf_wnlp_fp)

    DOY = df_out_pp.day.apply(lambda x: x.timetuple().tm_yday)
    df_out_pp.insert(0, "DOY", DOY)
    df_out_pp.to_excel(ofp.output_pp_fp)

    DOY = df_out_wlp.day.apply(lambda x: x.timetuple().tm_yday)
    df_out_wlp.insert(0, "DOY", DOY)
    df_out_wlp.to_excel(ofp.output_wlp_fp)

    DOY = df_out_wnlp.day.apply(lambda x: x.timetuple().tm_yday)
    df_out_wnlp.insert(0, "DOY", DOY)
    df_out_wnlp.to_excel(ofp.output_nwlp_fp)

    df_out_pp.to_excel(ofp.output_pp_fp)
    df_out_wlp.to_excel(ofp.output_wlp_fp)
    df_out_wnlp.to_excel(ofp.output_nwlp_fp)

    fig, ax = plt.subplots()
    ax.set_xlabel("Date (YYYY-MM-DD)")
    ax.set_ylabel("Yield (g DM m$^{-2}$ ground)")
    ax.plot(df_out_pp.day, df_out_pp.WSO, linestyle="-", color = 'g', label="Potential production")
    ax.plot(df_out_wlp.day, df_out_wlp.WSO, linestyle="-", color = 'b', label="Water-limited production")
    ax.plot(df_out_wnlp.day, df_out_wnlp.WSO, linestyle="-", color = 'r', label="Water-and-nutrient limited production")
    ax.legend()
    fig.autofmt_xdate()
    fig.savefig(ofp.fig_fp, dpi = 900)

if __name__ == "__main__":
    main()