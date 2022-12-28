/* eslint-disable react/button-has-type */
import { bool, func, node, string } from "prop-types";
import React from "react";
import { classNames } from "../utils";

function Button({ children, className, disabled, onClick, type, variant }) {
  return (
    <button
      className={classNames(
        "inline-flex w-fit items-center justify-center rounded-md border border-transparent shadow-sm transition-buttons duration-200 px-4 py-2 text-sm font-medium",
        "hover:shadow-lg",
        "focus:ring-offset-white focus:outline-none focus:ring-2 focus:ring-offset-2",
        variant === "primary"
          ? "bg-oxford-600 text-white hover:bg-oxford-700 focus:bg-oxford-700 focus:ring-oxford-500"
          : null,
        variant === "danger"
          ? "bg-bn-ribbon-600 text-white hover:bg-bn-ribbon-700 focus:bg-bn-ribbon-700 focus:ring-bn-ribbon-500"
          : null,
        className
      )}
      disabled={disabled}
      onClick={onClick}
      type={type}
    >
      {children}
    </button>
  );
}

export default Button;

Button.propTypes = {
  children: node.isRequired,
  className: string,
  disabled: bool,
  onClick: func,
  type: string,
  variant: string,
};

Button.defaultProps = {
  className: "",
  disabled: false,
  onClick: null,
  type: "button",
  variant: "primary",
};
