window.APP_CONFIG = {
  mode: new URLSearchParams(window.location.search).get("mode") || "direct",
  endpoints: {
    direct: {
      API_BASE: "http://127.0.0.1:8000/api",
      gateway: false,
    },
    gateway: {
      API_BASE: "http://127.0.0.1:8080/api",
      gateway: true,
    },
  },
};
