import React, { useState, useEffect, useRef } from "react";
import {
  FrameOptions,
  createEmbeddingContext,
} from "amazon-quicksight-embedding-sdk";

interface QuickSightEmbedProps {
  embedUrl: string;
}

const QuickSightEmbed: React.FC<QuickSightEmbedProps> = ({ embedUrl }) => {
  const containerRef = useRef<HTMLDivElement>(null); // ダッシュボードを埋め込むためのコンテナの参照
  const [isLoading] = useState(false); // 読み込み状態の管理

  useEffect(() => {
    if (containerRef.current && embedUrl) {
      const embedConsole = async () => {
        try {
          const options = {
            url: embedUrl,
            container: containerRef.current,
            resizeHeightOnSizeChangedEvent: true,
            withIframePlaceholder: true,
            onChange: console.log,
          } as FrameOptions;

          // Embedding SDKのコンテキストを非同期で作成
          const embedContext = await createEmbeddingContext();

          // コンテキストを使用してコンソールを埋め込む
          embedContext.embedConsole(options, {
            locale: "ja-JP",
          });

          // オプショナル: embedContextを使用してイベントリスナーを登録するなどの追加処理をここに記述
        } catch (error) {
          console.error("QuickSight embedding error:", error);
        }
      };
      embedConsole();
    }
  }, [embedUrl]);

  return (
    <div>
      {isLoading && (
        <div style={{ textAlign: "center" }}>読み込み中です...</div>
      )}
      <div
        ref={containerRef}
        style={{ width: "100%", height: isLoading ? "0" : "700px" }}
      />
    </div>
  );
};

export default QuickSightEmbed;
