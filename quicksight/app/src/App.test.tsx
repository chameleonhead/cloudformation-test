import { createContext, useContext } from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";

describe("App コンポーネント", () => {
  vi.mock("./context/AppContext", () => {
    const context = createContext({ token: "mock-token" });
    return {
      AuthProvider: context.Provider,
      useAuthContext: useContext(context),
    };
  });

  it("アプリケーションが正しくレンダリングされる", () => {
    render(
      <AuthProvider>
        <App />
      </AuthProvider>
    );
    const title = screen.getByText(/My App/i);
    expect(title).toBeInTheDocument();
  });

  // もしAppコンポーネント内で非同期処理（APIコールなど）を行っている場合、その完了を待つ必要があります。
  // 以下のテストケースは、非同期処理の完了を待つ例です。
  it("非同期処理の完了後、特定の要素が表示される", async () => {
    // APIのモックや非同期処理のモックを設定
    // 例: vi.spyOn(apiModule, 'fetchData').mockResolvedValue(mockData);
    render(
      <AuthProvider>
        <App />
      </AuthProvider>
    );
    // findBy* クエリは非同期処理が完了するのを待ちます。
    const dynamicElement = await screen.findByText(
      /非同期でロードされたテキスト/i
    );
    expect(dynamicElement).toBeInTheDocument();

    // モックのクリーンアップ
    // vi.restoreAllMocks();
  });

  // イベントに基づく挙動のテスト例
  it("通知アイコンをクリックすると通知メニューが表示される", async () => {
    render(
      <AuthProvider>
        <App />
      </AuthProvider>
    );
    const notificationIcon = screen.getByLabelText(/notifications/i);
    fireEvent.click(notificationIcon);

    const notificationMenu = await screen.findByRole("menu");
    expect(notificationMenu).toBeInTheDocument();
  });
});
