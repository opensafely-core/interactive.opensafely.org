import { useFormikContext } from "formik";
import { func, number } from "prop-types";
import React from "react";
import { useWizard } from "react-use-wizard";
import SelectCodelist from "../SelectCodelist";

function Step1({ codelistCount, setCodelistCount }) {
  const { isValid, setFieldValue, validateForm } = useFormikContext();
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
              // eslint-disable-next-line react/no-array-index-key
              key={i}
              description={
                i === 0
                  ? "Choose a codelist type, then search for a codelist"
                  : "Add another codelist to the request"
              }
              id={i}
              label={i === 0 ? "Select a codelist" : "Select another codelist"}
            />
          ))}
        {codelistCount < 2 ? (
          <button onClick={handleAddCodelist} type="button">
            Add another codelist
          </button>
        ) : (
          <button onClick={handleRemoveCodelist} type="button">
            Remove second codelist
          </button>
        )}
        <button onClick={handleNextPage} type="button">
          Next
        </button>
      </div>
    </div>
  );
}

export default Step1;

Step1.propTypes = {
  codelistCount: number.isRequired,
  setCodelistCount: func.isRequired,
};
