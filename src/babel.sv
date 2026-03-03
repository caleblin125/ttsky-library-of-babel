
module babel(
    input clk,
    input reset,
    input [4:0] charIn, //32 bit: [a-z][ .,!?;]
    input setSeed,
    output [4:0] charOut, //32 bit: [a-z][ .,!?;]
    output isWriting
);
    logic [7:0] counter;
    logic [4:0] state;
    logic [4:0] nextState0;
    logic [4:0] nextState1;
    logic [4:0] nextState2;
    always_comb begin : randgen //5 bit xorshift
        if(setSeed)begin
            nextState0 = charIn ^ (state << 2);
        end else begin
            nextState0 = state ^ (state << 2);
        end
    end

    logic pageGo;
    assign pageGo = (counter != 8'hFF);
    always @(posedge clk) begin : registers
        if(!reset)begin
            state <= 0;
            counter <= 0;
            nextState1 <= 0;
            nextState2 <= 0;
        end else if(pageGo) begin
            state <= nextState2 + nextState0;
            nextState1 <= nextState0 + 1;
            nextState2 <= nextState0 ^ (nextState1 << 3);
            if(!setSeed) begin
                counter <= counter + 1;
            end
        end
    end

    assign isWriting = pageGo;
    assign charOut = pageGo ? state : 0;

endmodule