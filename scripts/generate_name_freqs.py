# scripts/generate_name_freqs.py
import argparse, csv, collections, os
def detect_columns(header):
    lower = [h.lower() for h in header]
    name_cols = [i for i,h in enumerate(lower) if 'name' in h or 'vorname' in h or 'vornamen' in h]
    freq_cols = [i for i,h in enumerate(lower) if 'freq' in h or 'anz' in h or 'count' in h or 'number' in h]
    return name_cols, freq_cols
def aggregate_names(input_csv, out_map):
    with open(input_csv, newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        header = next(reader, [])
        name_cols, freq_cols = detect_columns(header)
        for row in reader:
            if not row: continue
            name = row[name_cols[0]].strip() if name_cols else row[0].strip()
            freq = 1
            if freq_cols:
                try:
                    freq = int(row[freq_cols[0]])
                except:
                    freq = 1
            lang = 'de'
            for i,h in enumerate(header):
                if 'kant' in h.lower() or 'canton' in h.lower():
                    canton = row[i].strip()
                    if canton.upper().startswith('TI'): lang='it'
                    elif canton.upper().startswith('VD') or canton.upper().startswith('GE') or canton.upper().startswith('FR'): lang='fr'
                    break
            out_map[lang][name] += freq
def write_counter_to_csv(counter, path):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['name','frequency'])
        for name, freq in counter.most_common():
            writer.writerow([name, freq])
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--firstnames', required=False)
    parser.add_argument('--lastnames', required=False)
    parser.add_argument('--outdir', default='data')
    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    names = {'de': collections.Counter(), 'fr': collections.Counter(), 'it': collections.Counter()}
    surnames = collections.Counter()
    if args.firstnames and os.path.exists(args.firstnames):
        aggregate_names(args.firstnames, names)
    if args.lastnames and os.path.exists(args.lastnames):
        with open(args.lastnames, newline='', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            header = next(reader, [])
            name_cols, freq_cols = detect_columns(header)
            for row in reader:
                if not row: continue
                name = row[name_cols[0]].strip() if name_cols else row[0].strip()
                freq = 1
                if freq_cols:
                    try:
                        freq = int(row[freq_cols[0]])
                    except:
                        freq = 1
                surnames[name] += freq
    write_counter_to_csv(surnames, os.path.join(args.outdir, 'surnames.csv'))
    write_counter_to_csv(names['de'], os.path.join(args.outdir, 'names_de.csv'))
    write_counter_to_csv(names['fr'], os.path.join(args.outdir, 'names_fr.csv'))
    write_counter_to_csv(names['it'], os.path.join(args.outdir, 'names_it.csv'))
    print('Wrote name files to', args.outdir)
if __name__ == '__main__':
    main()
