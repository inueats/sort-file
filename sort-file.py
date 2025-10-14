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
#    - このPythonスクリプト (`.py`ファイル) と、処理したいJSONファイル群
#      (`dummy_data_*.json`) を同じフォルダに置いてください。
#
# 2. ソート基準キーの指定:
#    - 下の「設定項目」セクションにある `TIMESTAMP_KEY` の値を、
#      ソートの基準にしたいタイムスタンプのキー名に変更します。
#    - このキーは、JSONファイル内の各レコードに含まれている必要があります。
#
#    【キーの指定例】
#    - 最上位のキーを使う場合:
#      TIMESTAMP_KEY = "fixedAt"
#      TIMESTAMP_KEY = "detectedAt"
#
#    - JSON内部のJSON(ネストされた)キーを使う場合 (ピリオドで区切ります):
#      TIMESTAMP_KEY = "reviewData.date"
#
# 3. ターミナルでスクリプトを実行:
#    - ターミナル（コマンドプロンプト）を開き、このファイルがあるフォルダに移動します。
#    - 次のコマンドを実行してください: python (このファイル名).py
#
# 4. 結果の確認:
#    - 実行が完了すると、`group_(指定したキー名)_01` のような名前のフォルダが10個作成されます。
#    - ファイルがタイムスタンプの昇順（古いものから新しいものへ）にソートされ、
#      10個のフォルダに均等に分割・格納されます。
# ==================================================================================


# --- 設定項目 ---
# ソートの基準にしたいタイムスタンプのキーをここで指定します。
# 例: "fixedAt"、"detectedAt"、"date"
# ネストされたキーの場合: "reviewData.date" のようにピリオドで区切って指定
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

def sort_and_distribute_files():
    """
    カレントディレクトリにあるJSONファイルを読み込み、指定されたタイムスタンプキーでソート後、
    10個の新しいフォルダに分割して保存する。
    """
    json_files = glob.glob('dummy_data_*.json')
    if not json_files:
        print("エラー: 処理対象のJSONファイルが見つかりません。")
        return

    print(f"{len(json_files)}個のJSONファイルが見つかりました。基準キー: '{TIMESTAMP_KEY}'")

    file_timestamps = []

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if not isinstance(data, list) or not data:
                    print(f"警告: {file_path} は空か、リスト形式ではありません。スキップします。")
                    continue

                timestamp_str = None
                for record in data:
                    # 指定されたキーを基に値を取得
                    ts_val = get_nested_value(record, TIMESTAMP_KEY)
                    if ts_val:
                        timestamp_str = ts_val
                        break
                
                if timestamp_str:
                    # タイムスタンプのフォーマットから小数点以下を7桁以上受け入れられるように修正
                    if '.' in timestamp_str:
                        base, frag = timestamp_str.split('.')
                        timestamp_str = f"{base}.{frag[:6]}" # マイクロ秒（6桁）に丸める
                        dt_format = '%Y-%m-%d %H:%M:%S.%f'
                    else:
                        dt_format = '%Y-%m-%d %H:%M:%S'

                    timestamp = datetime.strptime(timestamp_str, dt_format)
                    file_timestamps.append((timestamp, file_path))
                else:
                    print(f"警告: {file_path} 内に有効な '{TIMESTAMP_KEY}' が見つかりませんでした。スキップします。")

        except Exception as e:
            print(f"エラー: {file_path} の処理中に予期せぬエラーが発生しました: {e}")

    file_timestamps.sort(key=lambda x: x[0])

    sorted_files = [file_path for timestamp, file_path in file_timestamps]
    
    if len(sorted_files) < 10:
        print(f"エラー: ソート対象のファイルが{len(sorted_files)}個しかありません。10分割するには足りないため、処理を中断します。")
        return

    split_files = np.array_split(sorted_files, 10)

    print("\nファイルの分割を開始します...")
    for i, file_group in enumerate(split_files):
        folder_name = f"group_{TIMESTAMP_KEY}_{i+1:02d}"
        os.makedirs(folder_name, exist_ok=True)
        print(f"フォルダ '{folder_name}' を作成/確認し、{len(file_group)}個のファイルを移動します。")

        for file_path in file_group:
            try:
                shutil.move(file_path, os.path.join(folder_name, os.path.basename(file_path)))
            except Exception as e:
                print(f"エラー: {file_path} の移動中にエラーが発生しました: {e}")
    
    print("\n処理が正常に完了しました。")

if __name__ == "__main__":
    sort_and_distribute_files()