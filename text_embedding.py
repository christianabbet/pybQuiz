import os
import argparse
import ollama
import numpy as np
from tqdm import tqdm
from typing import Optional

from pybquiz.db.base import UnifiedTSVDB
from pybquiz.db.base import TriviaTSVDB, TriviaQ


def embedd(
    dataset: TriviaTSVDB, 
    id_subset: list[int],
    model_name: Optional[str] = "mxbai-embed-large",
):

    # Get embedding size
    result = ollama.embeddings(model=model_name, prompt="test")
            
    # Get item numbers
        
    # Infer new ones
    N_new = len(id_subset)
    F = len(result.get("embedding", []))
    z = np.zeros((N_new, F))
    y = [None]*N_new
    uuid = [None]*N_new
    model = [None]*N_new
    
    for i in tqdm(range(N_new)):
        # Get prompt
        batch = dataset[id_subset[i]]
        result = ollama.embeddings(
            model=model_name,
            prompt=batch.get(TriviaQ.KEY_QUESTION, "error"),
        )
        # Append results
        z[i] = result.get("embedding", [])
        y[i] = batch.get(TriviaQ.KEY_CATEGORY, None)
        uuid[i] = batch.get(TriviaQ.KEY_UUID, None)
        model[i] = batch.get("domain", None)
        
    # Return output
    return z, y, uuid, model

    
def main(args):

    # Get data and loader
    triviadb = UnifiedTSVDB(dbs=None)
    path_npz = os.path.join(args.cache, "embedding_trivia.npz")
    N = len(triviadb)
    
    # Load existing
    z, y, uuid, domain = [], [], [], []
    
    if os.path.exists(path_npz):
        print("Load existing data ...")
        data = np.load(path_npz, allow_pickle=True)["data"].item()
        z = data["z"]
        y = data["y"]
        uuid = data["uuid"]
        domain = data["domain"]

    # Infer dummy
    print("Check existing data ...")
    exists = [d[TriviaQ.KEY_UUID] in uuid for d in triviadb]
    id_subset = np.nonzero(np.logical_not(exists))[0]

    # Check if update is needed    
    if len(id_subset) != 0:
        # Get new embedding
        z_new, y_new, uuid_new, domain_new = embedd(dataset=triviadb, model_name=args.model, id_subset=id_subset)
        # Append embedding
        z = np.concatenate([z, z_new], axis=0)
        y = np.concatenate([y, y_new], axis=0)
        uuid = np.concatenate([uuid, uuid_new], axis=0)
        domain = np.concatenate([domain, domain_new], axis=0)
        
        # Sanity check
        assert len(z) == len(y) and len(z) == len(uuid) and len(z) == len(domain)
                
        # Save output
        print("Saving ...")
        np.savez_compressed(path_npz, data={"z": z, "y": y, "uuid": uuid, "domain": domain})

    print("Done")

if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='Text embedding',
        description='Embed text for feature description',
    )
    parser.add_argument('--model', default="mxbai-embed-large",
                        choices=['mxbai-embed-large', 'nomic-embed-text', 'all-minilm'],
                        help='Default embedding model (https://ollama.com/blog/embedding-models).')
    parser.add_argument('--cache', default=".cache",
                        help='Reference file for trianing.')    
    args = parser.parse_args()
    
    main(args=args)
    