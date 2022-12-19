import React from "react";
import { classNames } from "../utils";

const InputFeedback = ({ error }) =>
  error ? <div className={classNames("input-feedback")}>{error}</div> : null;

export default InputFeedback;
