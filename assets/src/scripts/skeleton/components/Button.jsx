import React from "react";
import { classNames } from "../utils";

function Button({
  children,
  className,
  size = "md",
  type = "button",
  variant,
  disabled,
  ...props
}) {
  return (
    <button
      className={classNames(
        "inline-flex items-center justify-center border border-transparent font-semibold rounded-md cursor-pointer transition-colors outline outline-offset-2 outline-transparent no-underline",
        size === "md" && "text-sm px-4 py-2",
        size === "lg" && "text-base px-5 py-3",
        variant === "primary" &&
          "text-white bg-oxford-600 hover:bg-oxford-500 focus:outline-oxford-100",
        variant === "success" &&
          "text-white bg-green-600 hover:bg-green-500 focus:outline-green-100",
        variant === "danger" &&
          "text-white bg-red-600 hover:bg-red-500 focus:outline-red-100",
        disabled && "cursor-not-allowed opacity-80 !bg-slate-600",
        className
      )}
      type={type}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button;
