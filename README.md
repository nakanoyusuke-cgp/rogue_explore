# rogue_explore
Rogueライクなダンジョンの探索が可能な強化学習向けのベンチマーク環境です。 \
\
一般的なローグライクゲームにあるような戦闘やアイテム鑑定などの要素はありませんが、行動回数の制限を表す「満腹度」の概念があります。 \
満腹度は初期値の100から毎ステップ減少し、0になると探索が打ち切られます。 \
満腹度はダンジョン内に落ちている食料アイテムを獲得し、コマンドによって使用することで最大まで回復することができます。

## 動作を確認した環境
- Python 3.8.16
- Tkinter 8.6.12

## 導入方法
```
git clone git@github.com:nakanoyusuke-cgp/rogue_explore.git
cd rogue_explore
pip install .
```

## サンプルプログラムについて
以下2種類のサンプルプログラムをご用意しています。
- `samples/random_action.py` \
  環境を読み込み、ランダムな行動を実行します。\
  導入が成功したかどうかの確認等にご利用ください。

- `samples/human_play.py` \
  キーボード入力により任意の行動を実行することができます。 \
  特定の状態遷移におけるシステム挙動の確認等にご利用ください。\
  操作方法などの詳細はプログラム内のコメントをご確認ください。 \
  また、こちらのプログラムの実行にはpythonパッケージ「readchar」が必要ですので、別途インストールしてください。 \
  `samples/requirement.txt`ファイルを使用してインストールしていただくことも可能です。

## Gymのバージョンについて
- Gymのバージョンは0.26.2を使用しています。
- Gymの更新が終了していたみたいなので、Gymnasium(0.27.1)対応版も作成しました。Gymnasium対応版のrogue_exploreは以下のコマンドからクローンしてください。
  ```
  git clone -b gymnasium git@github.com:nakanoyusuke-cgp/rogue_explore.git
  ```
- 以前のgymインタフェースも利用できるように、gym0.21に対応したバージョンも仮作成しました。こちらは以下のコマンドからクローンしてください。
  ```
  git clone -b for-gym0.21 git@github.com:nakanoyusuke-cgp/rogue_explore.git
  ```

## 更新履歴
2023/5/3 gym0.21に対応したバージョンを仮作成
2023/5/3 画像表現(symbols, gray_scale)に関わらず観測の次元数を統一するように変更 \
2023/2/23 gymnasium対応版を作成, readmeを更新 \
2023/2/20 公開
