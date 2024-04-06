// QuickSightEmbed.tsx
import React, { useEffect } from "react";
import {
  createEmbeddingContext,
  EmbeddingContextFrameOptions,
} from "amazon-quicksight-embedding-sdk";

interface QuickSightEmbedProps {
  embedUrl: string;
}

const QuickSightEmbed: React.FC<QuickSightEmbedProps> = ({ embedUrl }) => {
  useEffect(() => {
    const options = {
      url: embedUrl,
      container: document.getElementById("quicksight-embed"),
      scrolling: "no",
      height: "700px",
      width: "100%",
      locale: "ja-JP",
      footerPaddingEnabled: true,
    } as EmbeddingContextFrameOptions;

    createEmbeddingContext(options);
  }, [embedUrl]);

  return <div id="quicksight-embed" />;
};

export default QuickSightEmbed;
