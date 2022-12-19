import React from "react";
import { classNames } from "../utils";

const RadioButton = ({
  field: { name, value, onChange, onBlur },
  id,
  label,
  className,
  resetOnChange,
  ...props
}) => {
  const isChecked = id === value;
  return (
    <label
      htmlFor={id}
      className={classNames(
        "border rounded-md py-3 px-3 flex items-center justify-center text-sm font-semibold sm:flex-1 cursor-pointer focus:outline-none",
        isChecked ? "ring-2 ring-oxford-500" : null
      )}
    >
      <input
        name={name}
        id={id}
        type="radio"
        value={id} // could be something else for output?
        checked={isChecked}
        onChange={(e) => {
          onChange(e);
          resetOnChange(e);
        }}
        onBlur={onBlur}
        className="sr-only"
        {...props}
      />
      <span>{label}</span>
    </label>
  );
};

export default RadioButton;
