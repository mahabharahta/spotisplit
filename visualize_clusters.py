#!/usr/bin/env python3
"""
SpotiSplit Cluster Visualization
Візуалізує 20 кластерів у 20-вимірному просторі характеристик
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

# Налаштування для кращої візуалізації
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_cluster_data(csv_file="spotisplit_clusters_no_audio.csv"):
    """Завантажує дані кластерів з CSV файлу"""
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Завантажено {len(df)} треків з {len(df.columns)} колонками")
        print(f"🎯 Кількість кластерів: {df['cluster'].nunique()}")
        return df
    except FileNotFoundError:
        print(f"❌ Файл {csv_file} не знайдено")
        print("💡 Спочатку запустіть run_spotisplit_no_audio.py")
        return None

def create_feature_pairs_plot(df, max_features=8):
    """Створює графік всіх пар характеристик з розбивкою по кластерах"""
    
    # Вибір числових характеристик для візуалізації
    numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_features = [f for f in numeric_features if f != 'cluster']
    
    # Обмежуємо кількість характеристик для кращої читабельності
    if len(numeric_features) > max_features:
        # Вибираємо найбільш інформативні характеристики
        feature_importance = []
        for feature in numeric_features:
            # Розраховуємо варіацію між кластерами
            between_cluster_var = df.groupby('cluster')[feature].var().mean()
            within_cluster_var = df[feature].var()
            if within_cluster_var > 0:
                importance = between_cluster_var / within_cluster_var
                feature_importance.append((feature, importance))
        
        # Сортуємо за важливістю та вибираємо топ
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        selected_features = [f[0] for f in feature_importance[:max_features]]
    else:
        selected_features = numeric_features
    
    print(f"📊 Візуалізую {len(selected_features)} найважливіших характеристик:")
    for i, feature in enumerate(selected_features, 1):
        print(f"   {i}. {feature}")
    
    # Створюємо всі пари характеристик
    feature_pairs = list(combinations(selected_features, 2))
    n_pairs = len(feature_pairs)
    
    # Розраховуємо розмір сітки
    cols = min(4, n_pairs)
    rows = (n_pairs + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
    fig.suptitle(f'SpotiSplit: Візуалізація 20 кластерів у {len(selected_features)}-вимірному просторі', 
                 fontsize=16, fontweight='bold')
    
    # Якщо тільки один ряд або колонка
    if rows == 1:
        axes = axes.reshape(1, -1)
    if cols == 1:
        axes = axes.reshape(-1, 1)
    
    # Створюємо кольорову палітру для кластерів
    colors = plt.cm.tab20(np.linspace(0, 1, df['cluster'].nunique()))
    
    for idx, (feature1, feature2) in enumerate(feature_pairs):
        row = idx // cols
        col = idx % cols
        
        if rows == 1:
            ax = axes[col]
        elif cols == 1:
            ax = axes[row]
        else:
            ax = axes[row, col]
        
        # Створюємо scatter plot для кожної пари
        for cluster_id in sorted(df['cluster'].unique()):
            cluster_data = df[df['cluster'] == cluster_id]
            ax.scatter(cluster_data[feature1], cluster_data[feature2], 
                      c=[colors[cluster_id]], alpha=0.6, s=20, 
                      label=f'Cluster {cluster_id}' if idx == 0 else "")
        
        ax.set_xlabel(feature1.replace('_', ' ').title())
        ax.set_ylabel(feature2.replace('_', ' ').title())
        ax.set_title(f'{feature1} vs {feature2}')
        ax.grid(True, alpha=0.3)
        
        # Додаємо легенду тільки для першого графіка
        if idx == 0:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # Приховуємо порожні графіки
    for idx in range(n_pairs, rows * cols):
        row = idx // cols
        col = idx % cols
        if rows == 1:
            axes[col].set_visible(False)
        elif cols == 1:
            axes[row].set_visible(False)
        else:
            axes[row, col].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('spotisplit_feature_pairs.png', dpi=300, bbox_inches='tight')
    print(f"💾 Збережено графік: spotisplit_feature_pairs.png")
    plt.show()

def create_cluster_summary_heatmap(df):
    """Створює теплову карту середніх значень характеристик по кластерах"""
    
    # Вибір числових характеристик
    numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_features = [f for f in numeric_features if f != 'cluster']
    
    # Розраховуємо середні значення по кластерах
    cluster_means = df.groupby('cluster')[numeric_features].mean()
    
    # Нормалізуємо дані для кращої візуалізації
    cluster_means_normalized = (cluster_means - cluster_means.mean()) / cluster_means.std()
    
    # Створюємо теплову карту
    plt.figure(figsize=(16, 10))
    sns.heatmap(cluster_means_normalized.T, 
                annot=True, 
                cmap='RdBu_r', 
                center=0,
                fmt='.2f',
                cbar_kws={'label': 'Z-score (нормалізоване значення)'})
    
    plt.title('SpotiSplit: Теплова карта кластерів (нормалізовані середні значення)', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Номер кластера')
    plt.ylabel('Характеристики')
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig('spotisplit_cluster_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"💾 Збережено теплову карту: spotisplit_cluster_heatmap.png")
    plt.show()

def create_cluster_size_distribution(df):
    """Створює графік розподілу розмірів кластерів"""
    
    cluster_sizes = df['cluster'].value_counts().sort_index()
    
    plt.figure(figsize=(14, 8))
    
    # Створюємо bar plot
    bars = plt.bar(range(len(cluster_sizes)), cluster_sizes.values, 
                   color=plt.cm.tab20(np.linspace(0, 1, len(cluster_sizes))))
    
    # Додаємо підписи
    for i, (cluster_id, size) in enumerate(cluster_sizes.items()):
        plt.text(i, size + 5, str(size), ha='center', va='bottom', fontweight='bold')
    
    plt.title('SpotiSplit: Розподіл розмірів 20 кластерів', fontsize=16, fontweight='bold')
    plt.xlabel('Номер кластера')
    plt.ylabel('Кількість треків')
    plt.xticks(range(len(cluster_sizes)), [f'Cluster {i}' for i in cluster_sizes.index])
    plt.grid(True, alpha=0.3, axis='y')
    
    # Додаємо статистику
    total_tracks = len(df)
    avg_size = total_tracks / len(cluster_sizes)
    plt.axhline(y=avg_size, color='red', linestyle='--', alpha=0.7, 
                label=f'Середній розмір: {avg_size:.0f} треків')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('spotisplit_cluster_sizes.png', dpi=300, bbox_inches='tight')
    print(f"💾 Збережено графік розмірів: spotisplit_cluster_sizes.png")
    plt.show()

def create_feature_distributions(df, top_features=6):
    """Створює розподіли основних характеристик по кластерах"""
    
    # Вибір топ характеристик
    numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_features = [f for f in numeric_features if f != 'cluster']
    
    # Розраховуємо важливість характеристик
    feature_importance = []
    for feature in numeric_features:
        between_cluster_var = df.groupby('cluster')[feature].var().mean()
        within_cluster_var = df[feature].var()
        if within_cluster_var > 0:
            importance = between_cluster_var / within_cluster_var
            feature_importance.append((feature, importance))
    
    feature_importance.sort(key=lambda x: x[1], reverse=True)
    top_features_list = [f[0] for f in feature_importance[:top_features]]
    
    print(f"📊 Візуалізую розподіли топ-{top_features} характеристик:")
    for i, feature in enumerate(top_features_list, 1):
        print(f"   {i}. {feature}")
    
    # Створюємо subplots
    cols = min(3, top_features)
    rows = (top_features + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    fig.suptitle('SpotiSplit: Розподіли основних характеристик по кластерах', 
                 fontsize=16, fontweight='bold')
    
    if rows == 1:
        axes = axes.reshape(1, -1)
    if cols == 1:
        axes = axes.reshape(-1, 1)
    
    colors = plt.cm.tab20(np.linspace(0, 1, df['cluster'].nunique()))
    
    for idx, feature in enumerate(top_features_list):
        row = idx // cols
        col = idx % cols
        
        if rows == 1:
            ax = axes[col]
        elif cols == 1:
            ax = axes[row]
        else:
            ax = axes[row, col]
        
        # Створюємо box plot для кожної характеристики
        cluster_data = [df[df['cluster'] == cluster_id][feature].values 
                       for cluster_id in sorted(df['cluster'].unique())]
        
        bp = ax.boxplot(cluster_data, patch_artist=True)
        
        # Встановлюємо кольори для box plots
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title(f'{feature.replace("_", " ").title()}')
        ax.set_xlabel('Номер кластера')
        ax.set_ylabel('Значення')
        ax.grid(True, alpha=0.3)
        
        # Встановлюємо підписи осі X
        ax.set_xticklabels([f'Cluster {i}' for i in sorted(df['cluster'].unique())])
    
    # Приховуємо порожні графіки
    for idx in range(top_features, rows * cols):
        row = idx // cols
        col = idx % cols
        if rows == 1:
            axes[col].set_visible(False)
        elif cols == 1:
            axes[row].set_visible(False)
        else:
            axes[row, col].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('spotisplit_feature_distributions.png', dpi=300, bbox_inches='tight')
    print(f"💾 Збережено розподіли: spotisplit_feature_distributions.png")
    plt.show()

def create_3d_scatter_plot(df, feature1='popularity', feature2='duration_minutes', feature3='age_years'):
    """Створює 3D scatter plot для трьох основних характеристик"""
    
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    colors = plt.cm.tab20(np.linspace(0, 1, df['cluster'].nunique()))
    
    for cluster_id in sorted(df['cluster'].unique()):
        cluster_data = df[df['cluster'] == cluster_id]
        ax.scatter(cluster_data[feature1], cluster_data[feature2], cluster_data[feature3],
                  c=[colors[cluster_id]], alpha=0.6, s=20, label=f'Cluster {cluster_id}')
    
    ax.set_xlabel(feature1.replace('_', ' ').title())
    ax.set_ylabel(feature2.replace('_', ' ').title())
    ax.set_zlabel(feature3.replace('_', ' ').title())
    ax.set_title(f'SpotiSplit: 3D візуалізація кластерів\n{feature1} vs {feature2} vs {feature3}', 
                 fontsize=14, fontweight='bold')
    
    ax.legend(bbox_to_anchor=(1.15, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('spotisplit_3d_scatter.png', dpi=300, bbox_inches='tight')
    print(f"💾 Збережено 3D графік: spotisplit_3d_scatter.png")
    plt.show()

def main():
    """Основна функція"""
    print("🎵 SpotiSplit Cluster Visualization")
    print("=" * 50)
    
    # Завантажуємо дані
    df = load_cluster_data()
    if df is None:
        return
    
    print(f"\n📊 Статистика кластерів:")
    print(f"   Загальна кількість треків: {len(df)}")
    print(f"   Кількість кластерів: {df['cluster'].nunique()}")
    print(f"   Середній розмір кластера: {len(df) / df['cluster'].nunique():.1f}")
    print(f"   Мінімальний розмір кластера: {df['cluster'].value_counts().min()}")
    print(f"   Максимальний розмір кластера: {df['cluster'].value_counts().max()}")
    
    # Створюємо всі візуалізації
    print(f"\n🎨 Створення візуалізацій...")
    
    # 1. Розподіл розмірів кластерів
    print("1️⃣ Розподіл розмірів кластерів...")
    create_cluster_size_distribution(df)
    
    # 2. Теплова карта кластерів
    print("2️⃣ Теплова карта кластерів...")
    create_cluster_summary_heatmap(df)
    
    # 3. Розподіли характеристик
    print("3️⃣ Розподіли характеристик...")
    create_feature_distributions(df, top_features=9)
    
    # 4. Пари характеристик
    print("4️⃣ Пари характеристик...")
    create_feature_pairs_plot(df, max_features=8)
    
    # 5. 3D scatter plot
    print("5️⃣ 3D scatter plot...")
    create_3d_scatter_plot(df)
    
    print(f"\n🎉 Всі візуалізації створено та збережено!")
    print(f"📁 Файли збережено в поточній директорії:")
    print(f"   • spotisplit_cluster_sizes.png")
    print(f"   • spotisplit_cluster_heatmap.png")
    print(f"   • spotisplit_feature_distributions.png")
    print(f"   • spotisplit_feature_pairs.png")
    print(f"   • spotisplit_3d_scatter.png")

if __name__ == "__main__":
    main()
