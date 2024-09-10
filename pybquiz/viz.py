import numpy as np
from typing import Optional
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
from pycirclize import Circos
import pandas as pd
matplotlib.use('Agg') # set the backend before importing pyplot


def plot_umap(
    z: np.ndarray, 
    y: np.ndarray, 
    domain: np.ndarray,
    path: Optional[str] = "viz_embedding.png"
):
    
    # get number of db
    name_dbs = np.unique(domain)
    n_rows = len(name_dbs) // 2
    n_cols = np.ceil(len(name_dbs) / n_rows).astype(int)
    _, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(10*n_cols, 10*n_rows), sharex=True, sharey=True)
    
    # Flatten axis and remove axis
    axes = axes.ravel()
    [a.axis("off") for a in axes]
    
    for i, name_db in enumerate(name_dbs):
        # Get ids
        id_db = np.nonzero(domain == name_db)[0]
        id_db = np.random.permutation(id_db)
        y_db = y[id_db]
        # Plot results
        axes[i].set_title(name_db)
        palette = sns.color_palette("hls", len(np.unique(y_db)))
        sns.scatterplot(
            x=z[id_db, 0], y=z[id_db, 1], hue=y_db, style=y_db, ax=axes[i], palette=palette)

    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')
    plt.close()
        
    

def plot_chord(
    z: np.ndarray, 
    y: np.ndarray, 
    domain: np.ndarray,
    path: Optional[str] = "viz_chord.png",
    vth: Optional[float] = 0.5
):
    
    # Get columns features
    N = len(z)
    u_domain, _ = np.unique(domain, return_counts=True)
    label_2_idx = {d: {k: i for i, k in enumerate(np.unique(y[d==domain]))} for d in u_domain}
    idx_to_label = {d: {i: k for i, k in enumerate(np.unique(y[d==domain]))} for d in u_domain}

    # Initialize circos sectors
    sectors = {k: len(label_2_idx[k]) for k in u_domain}
    circos = Circos(sectors, space=10)

    print("Create sectors ...")
    for sector in circos.sectors:
        
        # Main track
        name_db = sector.name
        track = sector.add_track((80, 100), r_pad_ratio=0.1)

        # Compute similarity inner category
        idx_in = np.nonzero(domain == name_db)[0]
        z_in = z[idx_in]
        y_in = y[idx_in]
        sim_in = (z_in @ z_in.T) - np.eye(len(z_in))
        y_hat_in = y_in[sim_in.argmax(axis=0)]
        
        # Plot outer xticks
        n_labels_ = len(label_2_idx[name_db])
        x_labels_ = list(range(n_labels_))
        labels_ = [idx_to_label[name_db][p] for p in x_labels_]
        
        # Bar
        y_labels_ = [np.sum((l == y_in) & (y_in == y_hat_in))/np.sum(l == y_in) for l in labels_]
        track.bar(x_labels_, y_labels_)
        labels_ = [l.replace("Entertainment: ", "").replace("_", " ").capitalize() for l in labels_]
        
        track.xticks(
            x_labels_, 
            labels_,
            label_orientation="vertical",
            tick_length=0,
            label_margin=2,
        )
    
    circos.savefig(path)


    print("Create links ...")
    for i, ssrc in enumerate(sectors.keys()):
        for j, sdst in enumerate(sectors.keys()):
            # Not same to same connection
            if i == j:
                continue
            # Build connections
            idx_src = np.nonzero(domain == ssrc)[0]
            idx_dst = np.nonzero(domain == sdst)[0]
            
            sim = z[idx_src] @ z[idx_dst].T
            l_dst = y[idx_dst[sim.argmax(axis=1)]]
            l_src = y[idx_src]
            v_src_dst = sim.max(axis=1)
            
            # Other
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
                    i_src = label_2_idx[ssrc][l_src[k]]
                    i_dst = label_2_idx[sdst][l_dst[l]]
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

    circos.savefig(path)
