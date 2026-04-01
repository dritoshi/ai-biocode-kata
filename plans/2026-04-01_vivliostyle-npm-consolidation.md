# Vivliostyleビルド環境の整理

## Context

`package.json` と `node_modules` がルートと `build/` に重複している。依存パッケージは同一。`vivliostyle.config.js` はルート起点のパスを使用しているため、ルートに統一する。

## 2つのPDFパイプラインへの影響

| パイプライン | 依存 | 影響 |
|------------|------|------|
| pandoc PDF (`bash build/build_pdf.sh`) | pandoc + TeX Live のみ。npm不要 | なし |
| Vivliostyle (`npx vivliostyle build`) | ルートの `package.json` + `vivliostyle.config.js` | `build/` の重複を削除しても動作に影響なし |

## 変更

1. `build/package.json` → gitから削除
2. `build/package-lock.json` → gitから削除
3. `build/node_modules/` → ディスクから削除
4. ルートの `package-lock.json` → git追跡に追加（.gitignore更新済み）
5. `build/README.md` の Vivliostyle セクションを更新:「`cd build && npm install`」→「プロジェクトルートで `npm install`」

## 検証

1. `npx vivliostyle build` がルートで正常にPDF生成できること
2. `bash build/build_pdf.sh` が影響を受けないこと
