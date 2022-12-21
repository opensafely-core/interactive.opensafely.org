import { Field, useFormikContext } from "formik";
import React, { Fragment } from "react";
import { useWizard } from "react-use-wizard";
import codelists from "../../data/codelists.json";
import { classNames } from "../../utils";
import SelectCodelist from "../SelectCodelist";

function Step1X({ codelistCount, useCodelistCount }) {
  const {
    errors,
    isValid,
    setFieldTouched,
    setFieldValue,
    touched,
    validateForm,
    values,
  } = useFormikContext();
  const { nextStep } = useWizard();

  return (
    <>
      {codelistCount < 2 ? (
        <button
          type="button"
          onClick={() => useCodelistCount(codelistCount + 1)}
        >
          Add another codelist
        </button>
      ) : (
        <button
          type="button"
          onClick={() => useCodelistCount(codelistCount - 1)}
        >
          Remove second codelist
        </button>
      )}
      {Array(codelistCount)
        .fill(0)
        .map((_, i) => (
          <SelectCodelist key={i} id={i} />
        ))}
      <button
        type="button"
        onClick={() => {
          validateForm().then(() => {
            if (isValid) nextStep();
          });
        }}
      >
        Next
      </button>
    </>
  );
}

export default Step1X;
