import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from "@mui/material";

interface ErrorDialogProps {
  open: boolean;
  onClose: () => void;
  errorMessage: string;
  onOk: () => void;
}

const ErrorDialog: React.FC<ErrorDialogProps> = ({
  open,
  onClose,
  errorMessage,
  onOk,
}) => {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>エラーが発生しました</DialogTitle>
      <DialogContent>
        <DialogContentText>{errorMessage}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onOk} color="primary">
          OK
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ErrorDialog;
