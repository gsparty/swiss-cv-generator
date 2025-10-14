from src.data_loaders.bfs_pxweb import BFSClient
import json

def main():
    client = BFSClient('https://api.pxweb.bfs.admin.ch/')
    data = client.fetch('PopulationByCanton', params={})
    with open('data/raw/population_by_canton.json','w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__=='__main__':
    main()
