from typing import Optional
import umap
import os
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import argparse
import numpy as np
import seaborn as sns
from pycirclize import Circos
from pycirclize.utils import ColorCycler
matplotlib.use('Agg') # set the backend before importing pyplot


def plot_umap(df: pd.DataFrame, M: Optional[int] = 5000, seed: Optional[int] = 0):
    
    # Get columns features
    N = len(df)
    cfeat = [ c for c in df.columns if c.startswith("f")]
    
    # Fit values    
    reducer = umap.UMAP(random_state=seed)      
    rndState = np.random.RandomState(seed=seed)
    idrnd = rndState.permutation(N)[:M]
    
    X_train = df[cfeat].values
    print("Fit ...")
    reducer.fit(X_train[idrnd])
    print("Transform ...")
    z_train = reducer.transform(X_train)
    
    print("Plot ...")
    name_dbs = df["db"].unique()
    _, axes = plt.subplots(nrows=1, ncols=len(name_dbs), figsize=(10*len(name_dbs), 10))
    
    for i, name_db in enumerate(name_dbs):
        # Get ids
        iddb = df["db"] == name_db
        iddb = rndState.permutation(np.nonzero(iddb.values)[0])
        y = df.loc[iddb, "y"].values
        # Plot results
        axes[i].set_title(name_db)
        palette = sns.color_palette("hls", len(np.unique(y)))
        sns.scatterplot(
            x=z_train[iddb, 0], y=z_train[iddb, 1], hue=y, style=y, ax=axes[i], palette=palette)

    plt.tight_layout()
    plt.savefig("viz_embedding.png", bbox_inches='tight')
    plt.close()
        
    
def plot_circle(df: pd.DataFrame, vth: Optional[float] = 0.5):
    
    # Indexes
    df_index = df[["db", "y"]].value_counts(sort=False).reset_index()
    
    # Get columns features
    N = len(df)
    cfeat = [ c for c in df.columns if c.startswith("f")]
    labels = {n: {i: a for i, a in enumerate(d["y"].values)} for n, d in df_index.groupby("db")}
    llabels = {n: {a: i for i, a in enumerate(d["y"].values)} for n, d in df_index.groupby("db")}

    # Initialize circos sectors
    sectors = {k: v for k, v in df_index["db"].value_counts().items()}
    name2color = {'opentdb': "red", 'kenquizdb': "green", 'thetriviadb': "blue"}
    circos = Circos(sectors, space=20)

    print("Create sectors ...")
    for sector in circos.sectors:
        # Main track
        name_db = sector.name
        track = sector.add_track((80, 100), r_pad_ratio=0.1)

        idx_in = np.nonzero(df['db'].values == name_db)[0]

        # Compute similarity inner category
        x_in = df.loc[idx_in, cfeat].values
        y_in = df.loc[idx_in, 'y'].values
        sim_in = (x_in @ x_in.T) - np.eye(len(x_in))
        y_hat_in = y_in[sim_in.argmax(axis=0)]
        
        # Plot outer xticks
        nlab = len(labels[sector.name])
        pos = list(range(nlab))
        pos_l = [labels[sector.name][p] for p in pos]
        
        # Bar
        pos_y_in = [np.sum((l == y_in) & (y_in == y_hat_in))/np.sum(l == y_in) for l in pos_l]
        track.bar(pos, pos_y_in)
        
        track.xticks(
            pos, 
            [l.replace("Entertainment: ", "").replace("_", " ").capitalize() for l in pos_l],
            label_orientation="vertical",
            tick_length=0,
            label_margin=2,
        )

    print("Create links ...")
    for i, ssrc in enumerate(sectors.keys()):
        for j, sdst in enumerate(sectors.keys()):
            # Not same to same connection
            if i == j:
                continue
            # Build connections
            idx_src = np.nonzero(df['db'].values == ssrc)[0]
            idx_dst = np.nonzero(df['db'].values == sdst)[0]
            sim = df.loc[idx_src, cfeat].values @ df.loc[idx_dst, cfeat].values.T
            l_dst = df.loc[idx_dst[sim.argmax(axis=1)], 'y'].values
            l_src = df.loc[idx_src, 'y'].values
            v_src_dst = sim.max(axis=1)
            
            # sélsélsé
            df_sim = pd.DataFrame([l_src, l_dst, v_src_dst]).T
            df_sim.columns = ["src", "dst", "sim"]
            df_sim_cross = df_sim.pivot_table(values="sim", index="src", columns="dst", aggfunc="sum")
            df_sim_cross = df_sim_cross.div(df_sim["src"].value_counts(), axis=0)
            df_sim_cross.fillna(0, inplace=True)
            
            # Draw lines
            l_src = df_sim_cross.index
            l_dst = df_sim_cross.columns
            for k in range(len(l_src)):
                for l in range(len(l_dst)):
                    # Add thresh
                    v = df_sim_cross.iloc[k, l]
                    i_src = llabels[ssrc][l_src[k]]
                    i_dst = llabels[sdst][l_dst[l]]
                    # If link too small, cut it
                    if v < vth:
                        continue
                    scale = (v - vth) / (1 - vth)
                    circos.link(
                        (ssrc, i_src, i_src+scale*0.8), 
                        (sdst, i_dst, i_dst+scale*0.8), 
                        allow_twist=False,
                        alpha=v,
                        color=plt.get_cmap("magma")(1-scale),
                    )

    circos.savefig("viz_circos.png")

def main(args):
    
    # Create train set
    file_train = args.file_train
    
    if not os.path.exists(file_train):
        # Get data and loader
        raise FileNotFoundError
    
    # Reload data    
    df = pd.read_csv(file_train, sep="\t")

    # plot_umap(df=df)
    plot_circle(df=df)
    
    

if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='Text embedding',
        description='Embed text for feature description',
    )
    parser.add_argument('--file_train', default=".cache/clip_train.tsv.gz",
                        help='Reference file for trianing.')   
    args = parser.parse_args()
    
    main(args=args)
    