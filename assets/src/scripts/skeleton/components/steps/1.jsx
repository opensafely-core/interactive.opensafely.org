import { useFormikContext } from "formik";
import React from "react";
import { useWizard } from "react-use-wizard";
import SelectCodelist from "../SelectCodelist";

function Step1X({ codelistCount, setCodelistCount }) {
  const { isValid, setFieldValue, validateForm, setTouched } =
    useFormikContext();
  const { nextStep } = useWizard();

  const handleAddCodelist = () => {
    setCodelistCount(codelistCount + 1);
    setTimeout(() => validateForm(), 0);
  };

  const handleRemoveCodelist = () => {
    setFieldValue("codelistType1", undefined);
    setFieldValue("codelist1", undefined);
    setCodelistCount(codelistCount - 1);
    setTimeout(() => validateForm(), 0);
  };

  const handleNextPage = () => {
    validateForm().then(() => {
      if (isValid) {
        nextStep();
      }
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
      <button type="button" onClick={handleNextPage}>
        Next
      </button>
    </>
  );
}

export default Step1X;
