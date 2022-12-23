import { Field, useFormikContext } from "formik";
import { number, string } from "prop-types";
import React, { Fragment } from "react";
import { usePageData } from "../context/page-data-context";
import codelists from "../data/codelists.json";
import { classNames } from "../utils";
import Combobox from "./Combobox";

function SelectCodelist({ description, label, id }) {
  const codelist = `codelist${id}`;
  const codelistType = `codelistType${id}`;
  const codelistGroup = `codelistGroup${id}`;

  const {
    state: { data },
  } = usePageData();
  const {
    errors,
    setFieldError,
    setFieldTouched,
    setFieldValue,
    touched,
    validateForm,
    values,
  } = useFormikContext();

  const radioButtonChange = (item) => {
    if (item.id !== values[codelistType]) {
      setFieldValue(codelist, "");
      setFieldTouched(codelist, false);
    }
  };

  const handleSelectedItemChange = (item) => {
    setFieldError(codelist, undefined);
    setFieldValue(codelist, item?.selectedItem || undefined);
    setFieldTouched(codelist, true);
    setTimeout(() => validateForm(), 0);
  };

  return (
    <div aria-labelledby={codelistGroup} className="w-full mt-6" role="group">
      <h2 className="text-lg font-bold" id={codelistGroup}>
        {label}
      </h2>
      <p className="text-base text-slate-700">{description}</p>
      <fieldset className="mt-2">
        <legend className="sr-only">Select a codelist type</legend>
        <ul className="grid grid-cols-2 gap-2 mb-2">
          {codelists.map((item) => (
            <li key={`${codelistType}_${item.id}`}>
              <Field
                className="sr-only peer"
                id={`${codelistType}_${item.id}`}
                name={codelistType}
                onClick={() => radioButtonChange(item)}
                type="radio"
                value={item.id}
              />
              <label
                key={item.name}
                className={classNames(
                  "rounded-md bg-slate-50 border-2 shadow-md border-slate-300 py-2 px-1 flex items-center justify-center text-sm text-slate-800 font-semibold cursor-pointer transition-colors",
                  "hover:bg-oxford-100 hover:border-oxford-300",
                  "peer-focus:bg-green-50 peer-focus:border-green-100 peer-focus:ring-2 peer-focus:ring-offset-1 peer-focus:ring-offset-white peer-focus:ring-green-600",
                  "peer-checked:bg-white peer-checked:text-green-800 peer-checked:border-green-500",
                  "sm:flex-1"
                )}
                htmlFor={`${codelistType}_${item.id}`}
              >
                {item.name}
              </label>
            </li>
          ))}
        </ul>
      </fieldset>

      {errors[codelistType] && touched[codelistType] ? (
        <div>{errors[codelistType]}</div>
      ) : null}
      {codelists.map((item) => (
        <Fragment key={item.id}>
          {item.id === values[codelistType] ? (
            <>
              <Combobox
                choices={data}
                data={{
                  choices: "",
                  errors: "",
                  hint: "",
                  id: "",
                  label: "",
                  name: "",
                }}
                errors={[""]}
                handleSelectedItemChange={(i) => handleSelectedItemChange(i)}
                initialSelectedItem={values[codelist] || null}
              />
              {errors[codelist] && touched[codelist] ? (
                // eslint-disable-next-line no-console
                <div>{console.log(errors[codelist])}</div>
              ) : null}
            </>
          ) : null}
        </Fragment>
      ))}
    </div>
  );
}

export default SelectCodelist;

SelectCodelist.propTypes = {
  description: string.isRequired,
  label: string.isRequired,
  id: number.isRequired,
};
