
module babel(
    input clk,
    input reset,
    input [4:0] charIn, //32 bit: [a-z][ .,!?;]
    input setSeed,
    input [4:0] charOut //32 bit: [a-z][ .,!?;]
);
    logic [7:0] counter;
    logic [4:0] state;
    logic [4:0] nextState[2];
    always_comb begin : randgen //5 bit xorshift
        if(setSeed)begin
            nextState[0] = state ^ (state << 2);
        end else begin
            nextState[0] = charIn ^ (state << 2);
        end
        nextState[1] = nextState[0] ^ (nextState[0] >> 1);
        nextState[2] = nextState[1] ^ (nextState[1] << 3);
    end

    logic pageEnd;
    assign pageEnd = (counter == -1);
    always @(posedge clk) begin : registers
        if(reset)begin
            state <= 0;
            counter <= 0;
        end else if(pageEnd) begin
            state <= nextState[2];
            counter <= counter + 1;
        end
    end

    assign charOut = pageEnd ? 0 : state;

endmodule