// Basic test if request is sent to endpoint and response is OK
pm.test("response is ok", function () {
    // assert that the status code is 200
    pm.response.to.have.status(200);
});

// Test if Token authorization succeeded
pm.test("Authorization works", function () {
    // pm.response.to.be.error; 
    pm.response.to.not.have.jsonBody({ messsage: '401 UnAuthorized' });
});

// example using pm.response.to.be*
pm.test("response must have a body", function () {
    // assert that the response has a valid JSON body
    pm.response.to.be.json; // this assertion also checks if a body  exists, so the above check is not needed
});


pm.test("Test some values - type and date format", () => {
    _.each(pm.response.json(), (item) => {
        pm.expect(item.system).to.eql(false);
        pm.expect(item.created_at).to.be.a('string').match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[.]\d{3}Z$/)

    });
});