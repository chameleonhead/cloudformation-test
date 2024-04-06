import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import NotificationIcon from "./NotificationIcon";

// LocalStorageのモックを設定
beforeEach(() => {
  vi.spyOn(Storage.prototype, "getItem");
  vi.spyOn(Storage.prototype, "setItem");
});

describe("NotificationIcon コンポーネント", () => {
  it("正しくレンダリングされ、アイコンクリックでメニューが開く", async () => {
    render(<NotificationIcon />);
    const iconButton = screen.getByRole("button", { name: /notifications/i });
    expect(iconButton).toBeInTheDocument();

    fireEvent.click(iconButton);
    const menuItem = await screen.findByText(
      /This is a notification message 1/i
    );
    expect(menuItem).toBeInTheDocument();
  });

  it("メニューアイテムクリックで通知が既読としてLocalStorageに保存される", async () => {
    render(<NotificationIcon />);
    const iconButton = screen.getByRole("button", { name: /notifications/i });
    fireEvent.click(iconButton);

    const menuItem = await screen.findByText(
      /This is a notification message 1/i
    );
    fireEvent.click(menuItem);

    expect(localStorage.setItem).toHaveBeenCalledWith(
      "readNotifications",
      expect.stringContaining("1")
    );
    expect(localStorage.getItem).toHaveBeenCalledWith("readNotifications");
  });
});
