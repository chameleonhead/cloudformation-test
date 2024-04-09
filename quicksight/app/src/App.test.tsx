import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import App from "./App";

describe("App コンポーネント", () => {
  it("アプリケーションが正しくレンダリングされる", () => {
    vi.mock("./context/AuthContext", () => {
      return {
        useAuthContext: () => {
          return { token: "mock-token" };
        },
      };
    });
    render(<App />);
    const title = screen.getByText(/My App/i);
    expect(title).toBeInTheDocument();
    vi.restoreAllMocks();
  });

  it("トークンがない場合Loadingが表示される", async () => {
    vi.mock("./context/AuthContext", () => {
      return {
        useAuthContext: () => {
          return { token: null };
        },
      };
    });
    render(<App />);
    const title = screen.getByText(/My App/i);
    expect(title).toBeInTheDocument();
    const dynamicElement = await screen.findByText(/Loading/i);
    expect(dynamicElement).toBeInTheDocument();
    vi.restoreAllMocks();
  });

  // イベントに基づく挙動のテスト例
  it("通知アイコンをクリックすると通知メニューが表示される", async () => {
    vi.mock("./context/AuthContext", () => {
      return {
        useAuthContext: () => {
          return { token: null };
        },
      };
    });
    render(<App />);
    const notificationIcon = screen.getByLabelText(/notifications/i);
    fireEvent.click(notificationIcon);

    const notificationMenu = await screen.findByRole("menu");
    expect(notificationMenu).toBeInTheDocument();
    vi.restoreAllMocks();
  });
});
