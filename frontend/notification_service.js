(function initializeNotificationService(global) {
  "use strict";

  const ICONS = { success: "✓", error: "!", system: "i" };
  const DEFAULT_DURATION = 2800;

  class NotificationService {
    constructor() {
      this.sequence = 0;
    }

    get region() {
      return document.getElementById("notification-region");
    }

    notify(message, type = "system", options = {}) {
      const region = this.region;
      if (!region || !message) return null;
      const normalizedType = Object.hasOwn(ICONS, type) ? type : "system";
      const item = document.createElement("div");
      item.className = `notification notification-${normalizedType}`;
      item.dataset.notificationId = String(++this.sequence);
      item.setAttribute("role", normalizedType === "error" ? "alert" : "status");

      const icon = document.createElement("span");
      icon.className = "notification-icon";
      icon.textContent = ICONS[normalizedType];
      const text = document.createElement("span");
      text.className = "notification-text";
      text.textContent = message;
      const close = document.createElement("button");
      close.type = "button";
      close.className = "notification-close";
      close.setAttribute("aria-label", "关闭提示");
      close.textContent = "×";
      close.onclick = () => this.dismiss(item);
      item.append(icon, text, close);
      region.append(item);

      requestAnimationFrame(() => item.classList.add("visible"));
      const duration = Number.isFinite(options.duration) ? options.duration : DEFAULT_DURATION;
      if (duration > 0) item.dismissTimer = setTimeout(() => this.dismiss(item), duration);
      return item.dataset.notificationId;
    }

    success(message, options) { return this.notify(message, "success", options); }
    error(message, options) { return this.notify(message, "error", { duration: 4200, ...options }); }
    system(message, options) { return this.notify(message, "system", options); }

    dismiss(item) {
      if (!item || !item.isConnected) return;
      clearTimeout(item.dismissTimer);
      item.classList.remove("visible");
      setTimeout(() => item.remove(), 180);
    }

    clear() {
      this.region?.querySelectorAll(".notification").forEach((item) => this.dismiss(item));
    }
  }

  global.XiaoGNotification = new NotificationService();
})(window);