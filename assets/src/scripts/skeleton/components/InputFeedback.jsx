import { oneOfType, shape, string } from "prop-types";
import React from "react";
import { classNames } from "../utils";

function InputFeedback({ error }) {
  return error ? (
    <div className={classNames("input-feedback")}>{error}</div>
  ) : null;
}

export default InputFeedback;

InputFeedback.propTypes = {
  error: oneOfType([shape(), string]).isRequired,
};
