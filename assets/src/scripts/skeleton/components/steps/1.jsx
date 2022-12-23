import { useFormikContext } from "formik";
import React from "react";
import { useWizard } from "react-use-wizard";
import SelectCodelist from "../SelectCodelist";

function Step1({ codelistCount, setCodelistCount }) {
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
    <div className="grid grid-cols-2 gap-8">
      <div className="flex flex-col items-start gap-y-8">
        {Array(codelistCount)
          .fill(0)
          .map((_, i) => (
            <SelectCodelist
              description={
                i === 0
                  ? "Choose a codelist type, then search for a codelist"
                  : "Add another codelist to the request"
              }
              label={i === 0 ? "Select a codelist" : "Select another codelist"}
              key={i}
              id={i}
            />
          ))}
        {codelistCount < 2 ? (
          <button type="button" onClick={handleAddCodelist}>
            Add another codelist
          </button>
        ) : (
          <button type="button" onClick={handleRemoveCodelist}>
            Remove second codelist
          </button>
        )}
        <button type="button" onClick={handleNextPage}>
          Next
        </button>
      </div>
    </div>
  );
}

export default Step1;
