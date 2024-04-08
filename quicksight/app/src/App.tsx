import React, { useCallback, useEffect, useState } from "react";
import Navbar from "./components/Navbar";
import QuickSightEmbed from "./components/QuickSightEmbed";
import ErrorDialog from "./components/ErrorDialog";
import { useAuthContext } from "./context/AuthContext";

const App: React.FC = () => {
  const { token } = useAuthContext();
  const [embedUrl, setEmbedUrl] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isNetworkErrorOpen, setNetworkErrorOpen] = useState(false);
  const [isAuthErrorOpen, setAuthErrorOpen] = useState(false);

  // QuickSightの埋め込みURLを非同期で取得する仮の関数
  const fetchQuickSightEmbedUrl = useCallback(async () => {
    // ここで実際のAPI呼び出しを行い、埋め込みURLを取得する
    // この例では固定のURLを使用
    setIsLoading(true);
    try {
      const result = await fetch("/api/quicksight/embed-url", {
        headers: {
          Authorization: "Bearer " + token,
        },
      });
      const data = await result.json();
      console.log(data);
      setEmbedUrl(data.embedUrl);
    } catch (e) {
      setNetworkErrorOpen(true);
    } finally {
      setIsLoading(false);
    }
  }, [token, setIsLoading, setEmbedUrl, setNetworkErrorOpen]);

  useEffect(() => {
    if (token) {
      fetchQuickSightEmbedUrl();
    }
  }, [token, fetchQuickSightEmbedUrl]);

  const handleLogout = () => {
    console.log("ログアウト処理");
    // ここにログアウト処理を実装
  };

  // // エラーハンドリング関数
  // const handleNetworkError = () => {
  //   setNetworkErrorOpen(true);
  // };

  // const handleAuthError = () => {
  //   setAuthErrorOpen(true);
  // };

  return (
    <div>
      <Navbar onLogout={handleLogout} />
        {isLoading ? "Loading" : <QuickSightEmbed embedUrl={embedUrl} />}
      <ErrorDialog
        open={isNetworkErrorOpen}
        errorMessage="ネットワークエラーが発生しました。再試行してください。"
        onOk={() => setNetworkErrorOpen(false)}
        onClose={() => setNetworkErrorOpen(false)}
      />
      <ErrorDialog
        open={isAuthErrorOpen}
        errorMessage="認証エラーが発生しました。ページをリロードしてください。"
        onOk={() => window.location.reload()}
        onClose={() => setAuthErrorOpen(false)}
      />
    </div>
  );
};

export default App;
