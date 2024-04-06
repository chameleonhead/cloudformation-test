import React, { useState, useEffect } from "react";
import IconButton from "@mui/material/IconButton";
import NotificationsIcon from "@mui/icons-material/Notifications";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import ListItemText from "@mui/material/ListItemText";
import Badge from "@mui/material/Badge";

// 通知メッセージのサンプルデータ
const notifications = [
  { timestamp: 1, message: "This is a notification message 1" },
  { timestamp: 2, message: "This is a notification message 2" },
  { timestamp: 3, message: "This is a notification message 3" },
];

const NotificationIcon: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [readNotifications, setReadNotifications] = useState<{
    [key: number]: boolean;
  }>({});

  useEffect(() => {
    // LocalStorageから既読状態をロード
    const storedReadNotifications = localStorage.getItem("readNotifications");
    if (storedReadNotifications) {
      setReadNotifications(JSON.parse(storedReadNotifications));
    }
  }, []);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleRead = (timestamp: number) => {
    const newReadNotifications = { ...readNotifications, [timestamp]: true };
    setReadNotifications(newReadNotifications);
    // 既読状態をLocalStorageに保存
    localStorage.setItem(
      "readNotifications",
      JSON.stringify(newReadNotifications)
    );
  };

  const open = Boolean(anchorEl);
  const unreadCount = notifications.filter(
    (notification) => !readNotifications[notification.timestamp]
  ).length;

  return (
    <div>
      <IconButton
        aria-label="notifications"
        color="inherit"
        onClick={handleClick}
      >
        <Badge badgeContent={unreadCount} color="secondary">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Menu anchorEl={anchorEl} open={open} onClose={handleClose}>
        {notifications.map((notification) => (
          <MenuItem
            key={notification.timestamp}
            onClick={() => handleRead(notification.timestamp)}
          >
            <ListItemText primary={notification.message} />
          </MenuItem>
        ))}
      </Menu>
    </div>
  );
};

export default NotificationIcon;
