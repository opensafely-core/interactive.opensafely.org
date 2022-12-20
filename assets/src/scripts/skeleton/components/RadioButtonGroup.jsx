import React from "react";
import InputFeedback from "./InputFeedback";
import { classNames } from "../utils";

const RadioButtonGroup = ({
  value,
  error,
  touched,
  id,
  label,
  className,
  children,
  ...props
}) => {
  return (
    <div className={classNames(className)}>
      <fieldset>
        <legend className={props.hideLabel ? "sr-only" : null}>{label}</legend>
        <div className="grid grid-cols-2 gap-2">{children}</div>
        {touched && <div>{error}</div>}
      </fieldset>
    </div>
  );
};

export default RadioButtonGroup;
