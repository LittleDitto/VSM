import pandas as pd
import re
from collections import Counter

# Fungsi untuk preprocessing teks
def preprocess_text(text):
    # Hapus karakter selain huruf dan spasi
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Ubah teks menjadi huruf kecil
    text = text.lower()
    # Hapus vokal dari kata
    text = re.sub(r'[aeiou]', '', text)
    return text.strip()  # Menghilangkan spasi ekstra di awal atau akhir teks

# Fungsi untuk membuat word clusters sementara (tanpa normalisasi vokal)
def create_temp_word_clusters_raw(df):
    # Menggabungkan semua review menjadi satu teks
    all_text = ' '.join(df['review'])
    # Menghitung kata yang paling sering muncul
    word_counts = Counter(all_text.split())
    # Mengambil kata-kata yang paling sering muncul
    most_common_words = word_counts.most_common(20)  # Ubah angka 20 sesuai kebutuhan Anda
    return [word for word, count in most_common_words]

# Fungsi untuk membuat word clusters sementara (setelah dinormalisasi vokal)
def create_temp_word_clusters_normalized(df):
    # Menggabungkan semua review menjadi satu teks
    all_text = ' '.join(df['normalized_review'])
    # Menghitung kata yang paling sering muncul
    word_counts = Counter(all_text.split())
    # Mengambil kata-kata yang paling sering muncul
    most_common_words = word_counts.most_common(20)  # Ubah angka 20 sesuai kebutuhan Anda
    return [word for word, count in most_common_words]

# Fungsi untuk menghitung keberadaan word cluster dalam setiap review dengan iterrows
def compute_cluster_counts(df, clusters):
    cluster_columns = {word: [] for word in clusters}
    for index, row in df.iterrows():
        review = row['review']
        for word in clusters:
            if word in preprocess_text(review):
                cluster_columns[word].append(1)
            else:
                cluster_columns[word].append(0)
    return pd.DataFrame(cluster_columns)

# Fungsi untuk normalisasi word cluster
def normalize_clusters(clusters):
    normalized_clusters = {}
    for word in clusters:
        normalized_word = preprocess_text(word)
        if normalized_word in normalized_clusters:
            normalized_clusters[normalized_word] += clusters[word]
        else:
            normalized_clusters[normalized_word] = clusters[word]
    return normalized_clusters

# Baca dataset
df = pd.read_csv('datatest2.csv')

# Langkah 1: Buat word clusters sementara tanpa normalisasi vokal
temp_clusters_raw = create_temp_word_clusters_raw(df)

# Langkah 2: Hitung keberadaan word cluster tanpa normalisasi vokal dalam setiap review
temp_cluster_df_raw = compute_cluster_counts(df, temp_clusters_raw)

# Gabungkan dengan dataframe asli
df_temp_raw = pd.concat([df, temp_cluster_df_raw], axis=1)

# Langkah 3: Normalisasi kata-kata dalam dataset
df['normalized_review'] = df['review'].apply(preprocess_text)

# Langkah 4: Buat word clusters sementara setelah normalisasi vokal
temp_clusters_normalized = create_temp_word_clusters_normalized(df)

# Langkah 5: Hitung keberadaan word cluster setelah normalisasi vokal dalam setiap review
temp_cluster_df_normalized = compute_cluster_counts(df, temp_clusters_normalized)

# Gabungkan dengan dataframe asli
df_temp_normalized = pd.concat([df, temp_cluster_df_normalized], axis=1)

# Langkah 6: Normalisasi word cluster
normalized_clusters = normalize_clusters(Counter(temp_clusters_normalized))

# Langkah 7: Gabungkan nilai word cluster yang sudah dinormalisasi dengan word cluster asli
for original_word in temp_clusters_raw:
    normalized_word = preprocess_text(original_word)
    if normalized_word in normalized_clusters:
        df_temp_raw[original_word] = df_temp_raw[original_word] + temp_cluster_df_normalized[normalized_word]

# Simpan ke dalam file Excel
with pd.ExcelWriter('ulasan_combine.xlsx') as writer:
    df_temp_raw.to_excel(writer, sheet_name='Dataset Raw', index=False)
    df_temp_normalized.to_excel(writer, sheet_name='Dataset Normalized', index=False)
