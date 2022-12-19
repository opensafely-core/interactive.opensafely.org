import { useFormikContext } from "formik";
import React from "react";
import { useWizard } from "react-use-wizard";
import SelectCodelist from "../SelectCodelist";

function Step1X({ codelistCount, setCodelistCount }) {
  const { isValid, setFieldValue, validateForm } = useFormikContext();
  const { nextStep } = useWizard();

  const handleAddCodelist = () => {
    setCodelistCount(codelistCount + 1);
    setTimeout(() => {
      validateForm(), 100;
    });
  };

  const handleRemoveCodelist = () => {
    setCodelistCount(codelistCount - 1);
    setFieldValue("codelistType1", undefined);
    setFieldValue("codelist1", undefined);
    setTimeout(() => {
      validateForm(), 100;
    });
  };

  return (
    <>
      {codelistCount < 2 ? (
        <button type="button" onClick={handleAddCodelist}>
          Add another codelist
        </button>
      ) : (
        <button type="button" onClick={handleRemoveCodelist}>
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
