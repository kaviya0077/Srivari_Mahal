import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#6b21a8",
    },
    secondary: {
      main: "#facc15",
    },
    background: {
      default: "#f9fafb",
    },
  },
  typography: {
    fontFamily: "Roboto, sans-serif",
  },
});

export default theme;