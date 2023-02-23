# rogue_explore
Rogueっぽいダンジョンの探索が可能な強化学習向けのベンチマーク環境です。 \
\
戦闘やアイテム鑑定などの要素はありませんが、行動回数の制限を表す「満腹度」の概念があります。 \
満腹度は初期値の100から毎ステップ減少し、0になると探索が打ち切られます。 \
満腹度はダンジョン内に落ちている食料アイテムを獲得し、コマンドによって使用することで最大まで回復することができます。

(卒研で作成した強化学習環境をGymに対応させたものです。)

## 使用した環境
- Python 3.8.16
- Tkinter 8.6.12

## 導入方法
```
git clone git@github.com:nakanoyusuke-cgp/rogue_explore.git
cd rogue_explore
pip install .
```

## Gymのバージョンについて
- Gymのバージョンは0.26.2を使用しています。
- Gymの更新が終了していたみたいなので、Gymnasium(0.27.1)対応版も作成しました。Gymnasium対応版のrogue_exploreは以下のコマンドからクローンしてください。
  ```
  git clone -b gymnasium git@github.com:nakanoyusuke-cgp/rogue_explore.git
  ```

## 更新履歴
2023/2/23 gymnasium対応版を作成, readmeを更新 \
2023/2/20 公開
