import os
import glob
import json
import shutil
from datetime import datetime
import numpy as np

# ==================================================================================
# === 使い方 (How to Use) ===
# ==================================================================================
# 1. ファイルの準備:
#    - このPythonスクリプトと、処理したいJSONファイルを同じフォルダに置いてください。
#
# 2. ソート基準キーの指定:
#    - `TIMESTAMP_KEY` の値を、ソートの基準にしたいキー名に変更します。
#    - (変更点はこれ以降です)
#
# 3. ターミナルでスクリプトを実行:
#    - ターミナルから `python (このファイル名).py` を実行します。
#
# 4. 結果の確認:
#    - ファイルがタイムスタンプ順にソートされた後、全体の合計ファイルサイズを基に
#      11個のフォルダに「合計サイズがほぼ均等になるように」分割・格納されます。（ファイルサイズの端数で足りなくなるので10+1分割する）
# ==================================================================================

# --- 設定項目 ---
TIMESTAMP_KEY = "fixedAt" 
# ----------------

def get_nested_value(data_dict, key_string):
    """
    'a.b.c' のような文字列キーを使って、ネストされた辞書から値を取得する。
    """
    keys = key_string.split('.')
    value = data_dict
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def sort_and_distribute_files_by_size():
    """
    メインの処理を行う関数。
    JSONファイルをタイムスタンプでソート後、「合計ファイルサイズ」を基準に
    10個のフォルダに分割して保存します。
    """
    json_files = glob.glob('dummy_data_*.json')
    if not json_files:
        print("エラー: 処理対象のJSONファイルが見つかりません。")
        return

    print(f"{len(json_files)}個のJSONファイルが見つかりました。基準キー: '{TIMESTAMP_KEY}'")

    file_timestamps = []
    # (タイムスタンプ抽出のロジックは変更なし)
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list) or not data:
                print(f"警告: {file_path} は空か、リスト形式ではありません。スキップします。")
                continue
            timestamp_str = None
            for record in data:
                ts_val = get_nested_value(record, TIMESTAMP_KEY)
                if ts_val:
                    timestamp_str = ts_val
                    break
            if timestamp_str:
                if '.' in timestamp_str:
                    base, frag = timestamp_str.split('.')
                    timestamp_str = f"{base}.{frag[:6]}"
                    dt_format = '%Y-%m-%d %H:%M:%S.%f'
                else:
                    dt_format = '%Y-%m-%d %H:%M:%S'
                timestamp = datetime.strptime(timestamp_str, dt_format)
                file_timestamps.append((timestamp, file_path))
            else:
                print(f"警告: {file_path} 内に有効な '{TIMESTAMP_KEY}' が見つかりませんでした。スキップします。")
        except Exception as e:
            print(f"エラー: {file_path} の処理中に予期せぬエラーが発生しました: {e}")

    # --- タイムスタンプ順にソート ---
    file_timestamps.sort(key=lambda x: x[0])
    sorted_files = [file_path for timestamp, file_path in file_timestamps]
    
    if len(sorted_files) < 11:
        print(f"エラー: ソート対象のファイルが{len(sorted_files)}個しかありません。11分割するには足りないため、処理を中断します。")
        return

    # ============================================================================
    # === ここからが変更点：ファイルサイズを基準とした分割ロジック ===
    # ============================================================================
    
    # 1. 全ファイルの合計サイズを計算
    total_size = sum(os.path.getsize(f) for f in sorted_files)
    
    # 2. 1グループあたりの目標サイズを計算
    target_size_per_group = total_size / 11
    
    print(f"\n合計ファイルサイズ: {total_size / (1024*1024):.2f} MB")
    print(f"1グループあたりの目標サイズ: {target_size_per_group / (1024*1024):.2f} MB")

    # 3. ファイルを11個のグループに振り分ける
    all_groups = []
    current_group = []
    current_group_size = 0

    for file_path in sorted_files:
        current_group.append(file_path)
        current_group_size += os.path.getsize(file_path)
        
        # 現在のグループサイズが目標サイズを超え、かつ最後のグループでない場合
        # グループを確定し、次のグループの準備をする
        if current_group_size >= target_size_per_group and len(all_groups) < 9:
            all_groups.append(current_group)
            current_group = []
            current_group_size = 0
            
    # ループを抜けた後、残ったファイルを最後のグループとして追加
    if current_group:
        all_groups.append(current_group)

    # ============================================================================
    # === 変更点ここまで ===
    # ============================================================================

    print("\nファイルの分割を開始します...")
    for i, file_group in enumerate(all_groups):
        folder_name = f"group_{TIMESTAMP_KEY.replace('.', '_')}_{i+1:02d}"
        os.makedirs(folder_name, exist_ok=True)
        
        group_size_mb = sum(os.path.getsize(f) for f in file_group) / (1024*1024)
        print(f"フォルダ '{folder_name}' を作成/確認し、{len(file_group)}個のファイル (合計 {group_size_mb:.2f} MB) を移動します。")

        for file_path in file_group:
            try:
                shutil.move(file_path, os.path.join(folder_name, os.path.basename(file_path)))
            except Exception as e:
                print(f"エラー: {file_path} の移動中にエラーが発生しました: {e}")
    
    print("\n処理が正常に完了しました。")

if __name__ == "__main__":
    sort_and_distribute_files_by_size()
