import MockAdapter from "axios-mock-adapter";
import axios from "../../apis/axios";
import { getAuditBillingSummary } from "../../apis/auditService";
import { auditConstants } from "../../apis/apiUrlConstants";

describe("Audit API Service", () => {
    const mock = new MockAdapter(axios, { onNoMatch: "throwException" });

    beforeEach(() => {
        const mockUser = JSON.stringify({ token: "fake_token" });
        jest.spyOn(Storage.prototype, "getItem").mockImplementation((key) => {
            if (key === "user") return mockUser;
            return null;
        });
        mock.reset();
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    describe("getAuditBillingSummary", () => {
        const summary_type = "monthly";
        const target_date = "2024-10-10";

        it("should call onSuccess with response data when API call is successful", async () => {
            const responseData = { data: "billingSummaryData" };
            const onSuccess = jest.fn();
            const onError = jest.fn();
            mock.onGet(`${auditConstants.auditBilling}?summary_type=${summary_type}&target_date=${target_date}`)
                .reply(200, responseData);
            await getAuditBillingSummary({
                summary_type,
                target_date,
                onSuccess,
                onError,
            });
            expect(onSuccess).toHaveBeenCalledTimes(1);
            expect(onSuccess).toHaveBeenCalledWith(responseData);
            expect(onError).not.toHaveBeenCalled();
        });

        it("should call onError when API call fails", async () => {
            const errorResponse = { message: "Error retrieving data" };
            const onSuccess = jest.fn();
            const onError = jest.fn();
            mock.onGet(`${auditConstants.auditBilling}?summary_type=${summary_type}&target_date=${target_date}`)
                .reply(500, errorResponse);
            await getAuditBillingSummary({
                summary_type,
                target_date,
                onSuccess,
                onError,
            });
            expect(onError).toHaveBeenCalledTimes(1);
            expect(onError).toHaveBeenCalledWith(errorResponse);
            expect(onSuccess).not.toHaveBeenCalled();
        });
    });
});
