import React, { createContext, useContext, ReactNode } from "react";
import useAuth from "../hooks/useAuth";

// 認証コンテキストの型定義
interface AuthContextType {
  token: string | null;
  // 必要に応じて他の認証関連の状態や関数を追加
}

// 認証コンテキストの作成
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 認証プロバイダーコンポーネント
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const { token } = useAuth(); // useAuth フックを使用

  return (
    <AuthContext.Provider value={{ token }}>{children}</AuthContext.Provider>
  );
};

// カスタムフック: コンテキストを使用する
export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return context;
};
